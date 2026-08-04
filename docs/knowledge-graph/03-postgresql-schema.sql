-- =====================================================================================
-- PostgreSQL Schema — TP Risk Management SMS / Safety Knowledge Graph Platform
-- STATUS: DRAFT — controlled design document. Requires approval before implementation.
-- Parent: 01-enterprise-knowledge-graph-specification.md
-- Companion: 02-neo4j-node-relationship-model.md (Neo4j is a synced projection of this
--            schema, not a second source of truth — see EKG spec §4)
--
-- This is the system of record. Every classification-style column (category, hierarchy,
-- type, domain, method, source, mode) is a foreign key into ontology_concepts — never a
-- free-text string or a local CHECK-constrained enum. This is the single fix for V1's
-- core defect: four tools independently inventing four incompatible category lists.
-- =====================================================================================

CREATE EXTENSION IF NOT EXISTS pgcrypto; -- gen_random_uuid()

CREATE SCHEMA IF NOT EXISTS ontology;
CREATE SCHEMA IF NOT EXISTS safety;
CREATE SCHEMA IF NOT EXISTS regulatory;
CREATE SCHEMA IF NOT EXISTS provenance;

-- Standard updated_at maintenance (infrastructure convenience, not business logic)
CREATE OR REPLACE FUNCTION set_updated_at() RETURNS trigger AS $$
BEGIN NEW.updated_at = now(); RETURN NEW; END;
$$ LANGUAGE plpgsql;

-- =====================================================================================
-- ONTOLOGY SCHEMA — see PLATFORM_ARCHITECTURE_V2.md §3
-- =====================================================================================

CREATE TABLE ontology.schemes (
  id            uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  name          varchar(100) NOT NULL UNIQUE,   -- 'Hazard Taxonomy', 'Control Taxonomy', ...
  description   text,
  version       integer NOT NULL DEFAULT 1,
  created_at    timestamptz NOT NULL DEFAULT now()
);

CREATE TYPE ontology.concept_status AS ENUM ('draft','reviewed','approved','published','deprecated');

CREATE TABLE ontology.concepts (
  id                 uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  scheme_id          uuid NOT NULL REFERENCES ontology.schemes(id),
  parent_concept_id  uuid REFERENCES ontology.concepts(id),  -- BROADER
  pref_label         varchar(200) NOT NULL,
  definition         text,
  status             ontology.concept_status NOT NULL DEFAULT 'draft',
  source_ref         varchar(200),           -- e.g. 'bowtie-ccm-generator.html REF.controlHierarchy'
  effective_from     date NOT NULL DEFAULT current_date,
  effective_to       date,                   -- NULL = currently effective
  created_at         timestamptz NOT NULL DEFAULT now(),
  updated_at         timestamptz NOT NULL DEFAULT now(),
  CONSTRAINT concepts_effective_range CHECK (effective_to IS NULL OR effective_to > effective_from)
);
CREATE INDEX idx_concepts_scheme ON ontology.concepts(scheme_id);
CREATE INDEX idx_concepts_parent ON ontology.concepts(parent_concept_id);
CREATE TRIGGER trg_concepts_updated BEFORE UPDATE ON ontology.concepts
  FOR EACH ROW EXECUTE FUNCTION set_updated_at();

CREATE TYPE ontology.alias_type AS ENUM ('synonym','abbreviation','deprecated_term');

CREATE TABLE ontology.concept_aliases (
  id           uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  concept_id   uuid NOT NULL REFERENCES ontology.concepts(id) ON DELETE CASCADE,
  alias_text   varchar(200) NOT NULL,
  alias_type   ontology.alias_type NOT NULL DEFAULT 'synonym',
  UNIQUE (concept_id, alias_text)
);
CREATE INDEX idx_aliases_text ON ontology.concept_aliases(alias_text);

CREATE TYPE ontology.relation_type AS ENUM ('broader','narrower','related','equivalent');

CREATE TABLE ontology.concept_relations (
  id                  uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  subject_concept_id  uuid NOT NULL REFERENCES ontology.concepts(id),
  relation_type       ontology.relation_type NOT NULL,
  object_concept_id   uuid NOT NULL REFERENCES ontology.concepts(id),
  CHECK (subject_concept_id <> object_concept_id)
);

CREATE TABLE ontology.relationship_types (
  id               uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  name             varchar(100) NOT NULL UNIQUE,  -- e.g. 'MITIGATED_BY' — must match a Neo4j rel type
  domain_scheme_id uuid REFERENCES ontology.schemes(id),
  range_scheme_id  uuid REFERENCES ontology.schemes(id),
  description      text,
  cardinality      varchar(10) NOT NULL,          -- '1:1' | '1:N' | 'N:N'
  created_at       timestamptz NOT NULL DEFAULT now()
);

CREATE TYPE ontology.extraction_pattern_type AS ENUM ('regex','embedding-similarity','llm-prompt-instruction');
CREATE TYPE ontology.extraction_action AS ENUM ('auto-accept','flag-for-review','reject');

CREATE TABLE ontology.extraction_rules (
  id                   uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  target_concept_id    uuid NOT NULL REFERENCES ontology.concepts(id),
  pattern_type         ontology.extraction_pattern_type NOT NULL,
  confidence_threshold numeric(4,3) NOT NULL CHECK (confidence_threshold BETWEEN 0 AND 1),
  action               ontology.extraction_action NOT NULL,
  example_positive     text,
  example_negative     text,
  created_at           timestamptz NOT NULL DEFAULT now()
);

-- =====================================================================================
-- SAFETY SCHEMA — core entities, PLATFORM_ARCHITECTURE_V2.md §5
-- =====================================================================================

-- Minimal identity — full AuthN/AuthZ is a separate concern (architecture §2 AuthZ
-- component), not designed here. This table is the accountability target for
-- ownership fields (WHS s27 officer due diligence; briefing doc "control ownership").
CREATE TABLE safety.persons (
  id          uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  name        varchar(200) NOT NULL,
  role_title  varchar(200),
  email       varchar(320) UNIQUE,
  created_at  timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE safety.parks (
  id    uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  name  varchar(100) NOT NULL UNIQUE     -- 'Movie World', 'Wet\'n\'Wild Gold Coast', ...
);

CREATE TABLE safety.assets (
  id                  uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  name                varchar(300) NOT NULL,
  park_id             uuid REFERENCES safety.parks(id),
  asset_type_concept_id uuid REFERENCES ontology.concepts(id),   -- Asset taxonomy
  iso55000_class      varchar(100),        -- TO BE CONFIRMED
  status              varchar(30) NOT NULL DEFAULT 'active',
  created_at          timestamptz NOT NULL DEFAULT now(),
  updated_at          timestamptz NOT NULL DEFAULT now()
);
CREATE TRIGGER trg_assets_updated BEFORE UPDATE ON safety.assets
  FOR EACH ROW EXECUTE FUNCTION set_updated_at();

CREATE TABLE safety.documents (
  id                 uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  filename           varchar(500) NOT NULL,
  mime_type          varchar(100),
  blob_url           text NOT NULL,        -- Azure Blob Storage pointer
  uploaded_at        timestamptz NOT NULL DEFAULT now(),
  extraction_status  varchar(20) NOT NULL DEFAULT 'pending'
                     CHECK (extraction_status IN ('pending','processing','extracted','failed','reviewed')),
  source_hash        varchar(128) UNIQUE   -- dedup guard
);

CREATE TABLE safety.hazards (
  id                        uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  asset_id                  uuid REFERENCES safety.assets(id),   -- nullable: enterprise-wide hazards not yet asset-bound
  name                      varchar(300) NOT NULL,
  description               text NOT NULL,
  exposure_pathway          text,
  possible_consequence      text,
  category_concept_id       uuid REFERENCES ontology.concepts(id),   -- Hazard taxonomy
  energy_source_concept_id  uuid REFERENCES ontology.concepts(id),   -- Energy Source taxonomy
  date_identified           date NOT NULL DEFAULT current_date,
  owner_person_id           uuid REFERENCES safety.persons(id),
  created_at                timestamptz NOT NULL DEFAULT now(),
  updated_at                timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX idx_hazards_asset ON safety.hazards(asset_id);
CREATE INDEX idx_hazards_category ON safety.hazards(category_concept_id);
CREATE TRIGGER trg_hazards_updated BEFORE UPDATE ON safety.hazards
  FOR EACH ROW EXECUTE FUNCTION set_updated_at();

CREATE TABLE safety.risks (
  id                    uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  hazard_id             uuid NOT NULL REFERENCES safety.hazards(id),
  description           text NOT NULL,
  cause                 text,
  inherent_likelihood   smallint CHECK (inherent_likelihood BETWEEN 1 AND 5),
  inherent_consequence  smallint CHECK (inherent_consequence BETWEEN 1 AND 5),
  inherent_rating       varchar(10),   -- derived — see 07-inference-rules-catalogue.md R1
  current_likelihood    smallint CHECK (current_likelihood BETWEEN 1 AND 5),
  current_consequence   smallint CHECK (current_consequence BETWEEN 1 AND 5),
  current_rating        varchar(10),   -- derived
  target_likelihood     smallint CHECK (target_likelihood BETWEEN 1 AND 5),
  target_consequence    smallint CHECK (target_consequence BETWEEN 1 AND 5),
  sfarp_justification   text,
  status                varchar(20) NOT NULL DEFAULT 'Open' CHECK (status IN ('Open','Under Review','Closed')),
  review_date           date,
  created_at            timestamptz NOT NULL DEFAULT now(),
  updated_at            timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX idx_risks_hazard ON safety.risks(hazard_id);
CREATE INDEX idx_risks_rating ON safety.risks(current_rating);
CREATE TRIGGER trg_risks_updated BEFORE UPDATE ON safety.risks
  FOR EACH ROW EXECUTE FUNCTION set_updated_at();

CREATE TABLE safety.consequences (
  id                  uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  risk_id             uuid NOT NULL REFERENCES safety.risks(id),
  description         text NOT NULL,
  domain_concept_id   uuid REFERENCES ontology.concepts(id),   -- Consequence taxonomy
  severity            smallint CHECK (severity BETWEEN 1 AND 5),
  flag_608b           boolean NOT NULL DEFAULT false
);

CREATE TABLE safety.controls (
  id                    uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  risk_id               uuid NOT NULL REFERENCES safety.risks(id),
  description           text NOT NULL,
  control_type          varchar(20) NOT NULL CHECK (control_type IN ('Prevention','Mitigation')),
  hierarchy_concept_id  uuid REFERENCES ontology.concepts(id),   -- Control taxonomy
  classification        varchar(20) CHECK (classification IN ('Control','Support','Verification')),
  gate_1                boolean, gate_2 boolean, gate_3 boolean,  -- 08-critical-control-assurance-model.md §2 (GOHS-REF-SMS-001 3-gate classification test)
  eia_effective         boolean,   -- Guide Table 2 "Tests for an effective control" (LOPA-derived) — 08-critical-control-assurance-model.md §4a
  eia_independent       boolean,
  eia_auditable         boolean,
  effectiveness_rating  varchar(30),
  owner_person_id       uuid REFERENCES safety.persons(id),
  created_at            timestamptz NOT NULL DEFAULT now(),
  updated_at            timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX idx_controls_risk ON safety.controls(risk_id);
CREATE TRIGGER trg_controls_updated BEFORE UPDATE ON safety.controls
  FOR EACH ROW EXECUTE FUNCTION set_updated_at();

CREATE TABLE safety.critical_controls (
  control_id            uuid PRIMARY KEY REFERENCES safety.controls(id),
  farsi_functionality   smallint CHECK (farsi_functionality BETWEEN 1 AND 5),
  farsi_availability    smallint CHECK (farsi_availability BETWEEN 1 AND 5),
  farsi_reliability     smallint CHECK (farsi_reliability BETWEEN 1 AND 5),
  farsi_survivability   smallint CHECK (farsi_survivability BETWEEN 1 AND 5),
  farsi_interdependency smallint CHECK (farsi_interdependency BETWEEN 1 AND 5),  -- corrected from "interaction" — confirmed FARSI = Functionality/Availability/Reliability/Survivability/Interdependency per WHSQ Guide 2021 §5, §9.2.2.1
  farsi_score           numeric(3,2) GENERATED ALWAYS AS (
                           (COALESCE(farsi_functionality,0) + COALESCE(farsi_availability,0) +
                            COALESCE(farsi_reliability,0)  + COALESCE(farsi_survivability,0) +
                            COALESCE(farsi_interdependency,0)) / 5.0
                         ) STORED,
  created_at             timestamptz NOT NULL DEFAULT now(),
  updated_at             timestamptz NOT NULL DEFAULT now()
);
CREATE TRIGGER trg_criticalcontrols_updated BEFORE UPDATE ON safety.critical_controls
  FOR EACH ROW EXECUTE FUNCTION set_updated_at();

CREATE TABLE safety.failure_modes (
  id               uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  control_id       uuid NOT NULL REFERENCES safety.controls(id),
  description      text NOT NULL,
  mode_concept_id  uuid REFERENCES ontology.concepts(id)   -- Failure Mode taxonomy
);

CREATE TABLE safety.performance_standards (
  id                   uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  critical_control_id  uuid NOT NULL REFERENCES safety.critical_controls(control_id),
  requirement_text     text NOT NULL,
  measurable_criteria  text,
  created_at           timestamptz NOT NULL DEFAULT now(),
  updated_at           timestamptz NOT NULL DEFAULT now()
);
CREATE TRIGGER trg_perfstd_updated BEFORE UPDATE ON safety.performance_standards
  FOR EACH ROW EXECUTE FUNCTION set_updated_at();

CREATE TABLE safety.verification_activities (
  id                      uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  performance_standard_id uuid NOT NULL REFERENCES safety.performance_standards(id),
  method_concept_id       uuid REFERENCES ontology.concepts(id),   -- Verification taxonomy
  frequency               varchar(30),          -- Daily/Weekly/Fortnightly/Monthly/Quarterly/Annual/Biennial/Other
  due_date                date,
  last_completed          date,
  performed_by_person_id  uuid REFERENCES safety.persons(id),
  result                  text,
  created_at              timestamptz NOT NULL DEFAULT now(),
  updated_at              timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX idx_verification_due ON safety.verification_activities(due_date);
CREATE TRIGGER trg_verification_updated BEFORE UPDATE ON safety.verification_activities
  FOR EACH ROW EXECUTE FUNCTION set_updated_at();

CREATE TABLE safety.evidence (
  id                       uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  type_concept_id          uuid REFERENCES ontology.concepts(id),   -- Evidence taxonomy
  verification_activity_id uuid REFERENCES safety.verification_activities(id),
  source_document_id       uuid REFERENCES safety.documents(id),
  uploaded_by_person_id    uuid REFERENCES safety.persons(id),
  uploaded_at              timestamptz NOT NULL DEFAULT now(),
  linked_entity_type       varchar(50),   -- polymorphic pointer, e.g. 'hazard' | 'control' | 'incident'
  linked_entity_id         uuid
);
CREATE INDEX idx_evidence_linked ON safety.evidence(linked_entity_type, linked_entity_id);

CREATE TABLE safety.safety_case_claims (
  id                    uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  hazard_id             uuid REFERENCES safety.hazards(id),
  critical_control_id   uuid REFERENCES safety.critical_controls(control_id),
  claim_text            text NOT NULL,
  assurance_status      varchar(30) NOT NULL DEFAULT 'draft',
  created_at            timestamptz NOT NULL DEFAULT now(),
  updated_at            timestamptz NOT NULL DEFAULT now(),
  CHECK (hazard_id IS NOT NULL OR critical_control_id IS NOT NULL)
);
CREATE TRIGGER trg_claims_updated BEFORE UPDATE ON safety.safety_case_claims
  FOR EACH ROW EXECUTE FUNCTION set_updated_at();

CREATE TABLE safety.safety_case_claim_evidence (
  claim_id    uuid NOT NULL REFERENCES safety.safety_case_claims(id),
  evidence_id uuid NOT NULL REFERENCES safety.evidence(id),
  PRIMARY KEY (claim_id, evidence_id)
);

CREATE TABLE regulatory.requirements (
  id                       uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  source_concept_id        uuid REFERENCES ontology.concepts(id),  -- Regulatory ontology scheme
  clause_ref               varchar(100),
  text                     text,
  applies_to_entity_type   varchar(50),
  status                   varchar(20) NOT NULL DEFAULT 'TO_BE_CONFIRMED',
  created_at               timestamptz NOT NULL DEFAULT now(),
  updated_at               timestamptz NOT NULL DEFAULT now()
);
CREATE TRIGGER trg_requirements_updated BEFORE UPDATE ON regulatory.requirements
  FOR EACH ROW EXECUTE FUNCTION set_updated_at();

CREATE TABLE safety.safety_case_claim_requirements (
  claim_id       uuid NOT NULL REFERENCES safety.safety_case_claims(id),
  requirement_id uuid NOT NULL REFERENCES regulatory.requirements(id),
  PRIMARY KEY (claim_id, requirement_id)
);

-- Trigger Action Response Plan — briefing doc §5.7, formalized in
-- 08-critical-control-assurance-model.md §5 (net-new: no V1 equivalent)
CREATE TABLE safety.trigger_action_response_plans (
  id                    uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  critical_control_id   uuid NOT NULL REFERENCES safety.critical_controls(control_id),
  trigger_condition     text NOT NULL,       -- e.g. "2 consecutive overdue verifications (R3)"
  trigger_source_rule   varchar(10),         -- inference rule ID from 07-inference-rules-catalogue.md, e.g. 'R3','R5'
  required_action       text NOT NULL,
  response_owner_person_id uuid REFERENCES safety.persons(id),
  escalation_level      varchar(30) NOT NULL DEFAULT 'supervisor'
                        CHECK (escalation_level IN ('supervisor','manager','executive')),
  status                varchar(20) NOT NULL DEFAULT 'active' CHECK (status IN ('active','triggered','resolved','retired')),
  created_at            timestamptz NOT NULL DEFAULT now(),
  updated_at            timestamptz NOT NULL DEFAULT now()
);
CREATE TRIGGER trg_tarp_updated BEFORE UPDATE ON safety.trigger_action_response_plans
  FOR EACH ROW EXECUTE FUNCTION set_updated_at();

-- =====================================================================================
-- SAFETY CASE DEMONSTRATION MODEL — 11-safety-case-demonstration-model.md
-- Device boundary, ADH→ADI pathway, Safety Assessment, Claim→Argument→Evidence,
-- Monitoring, Demonstration Engine, Management of Change. Added following review
-- against the WHSQ Guide for major amusement parks: Preparing a safety case (2021),
-- read directly (2026-08-03).
-- =====================================================================================

-- Device description fields confirmed required by Guide §8.3
ALTER TABLE safety.assets ADD COLUMN is_amusement_device boolean NOT NULL DEFAULT false;
ALTER TABLE safety.assets ADD COLUMN manufacturer varchar(200);
ALTER TABLE safety.assets ADD COLUMN as3533_device_class varchar(50);            -- AS/NZS 3533.1-2009 cl.2.1
ALTER TABLE safety.assets ADD COLUMN plant_design_registration_number varchar(100);
ALTER TABLE safety.assets ADD COLUMN year_manufactured_or_commissioned integer;
ALTER TABLE safety.assets ADD COLUMN previous_names text[];
ALTER TABLE safety.assets ADD COLUMN modification_history text;

CREATE TABLE safety.device_boundaries (
  id                    uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  asset_id              uuid NOT NULL REFERENCES safety.assets(id),
  boundary_description  text NOT NULL,
  includes_description  text,
  excludes_description  text,
  created_at            timestamptz NOT NULL DEFAULT now(),
  updated_at            timestamptz NOT NULL DEFAULT now()
);
CREATE TRIGGER trg_boundaries_updated BEFORE UPDATE ON safety.device_boundaries
  FOR EACH ROW EXECUTE FUNCTION set_updated_at();

CREATE TABLE safety.interfaces (
  id               uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  boundary_id      uuid NOT NULL REFERENCES safety.device_boundaries(id),
  interface_type   varchar(30) NOT NULL CHECK (interface_type IN
                    ('external_hazard','internal_hazard','worker_interaction',
                     'patron_interaction','supporting_system','utility','environment')),
  description      text NOT NULL
);

-- ADH → Loss of Control → Credible Event → ADI → Serious Risk pathway
-- (specialization of Hazard → Risk, active only where hazards.is_adh = true —
-- 11-safety-case-demonstration-model.md §3)
ALTER TABLE safety.hazards ADD COLUMN is_adh boolean NOT NULL DEFAULT false;
ALTER TABLE safety.hazards ADD COLUMN device_boundary_id uuid REFERENCES safety.device_boundaries(id);
ALTER TABLE safety.risks   ADD COLUMN is_serious_risk boolean NOT NULL DEFAULT false;
ALTER TABLE safety.risks   ADD COLUMN serious_risk_justification text;

CREATE TABLE safety.credible_events (
  id                          uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  hazard_id                   uuid NOT NULL REFERENCES safety.hazards(id),
  risk_id                     uuid REFERENCES safety.risks(id),   -- GIVES_RISE_TO, once assessed
  description                 text NOT NULL,
  loss_of_control_description text,
  is_adi                      boolean NOT NULL DEFAULT false,
  created_at                  timestamptz NOT NULL DEFAULT now(),
  updated_at                  timestamptz NOT NULL DEFAULT now()
);
CREATE TRIGGER trg_credible_events_updated BEFORE UPDATE ON safety.credible_events
  FOR EACH ROW EXECUTE FUNCTION set_updated_at();

-- Safety Assessment (owning/scoping entity — 11-safety-case-demonstration-model.md §4)
CREATE TABLE safety.safety_assessments (
  id                          uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  device_boundary_id          uuid NOT NULL REFERENCES safety.device_boundaries(id),
  scope_description           text NOT NULL,
  serious_risk_threshold_note text,   -- operator's own documented interpretation (Guide §7.5 — deliberately not a fixed regulatory number)
  unmitigated_risk_method     text,   -- Guide §9 point 1
  status                      varchar(20) NOT NULL DEFAULT 'draft',
  prepared_by_person_id       uuid REFERENCES safety.persons(id),
  assessment_date             date,
  created_at                  timestamptz NOT NULL DEFAULT now(),
  updated_at                  timestamptz NOT NULL DEFAULT now()
);
CREATE TRIGGER trg_safety_assessments_updated BEFORE UPDATE ON safety.safety_assessments
  FOR EACH ROW EXECUTE FUNCTION set_updated_at();
CREATE TABLE safety.safety_assessment_hazards (       -- COVERS
  safety_assessment_id uuid NOT NULL REFERENCES safety.safety_assessments(id),
  hazard_id             uuid NOT NULL REFERENCES safety.hazards(id),
  PRIMARY KEY (safety_assessment_id, hazard_id)
);

-- Claim → Argument → Evidence (GSN-grounded — 11-safety-case-demonstration-model.md §5)
CREATE TABLE safety.safety_arguments (
  id                    uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  claim_id              uuid NOT NULL REFERENCES safety.safety_case_claims(id),
  argument_text         text NOT NULL,
  sequence              integer NOT NULL DEFAULT 1,
  created_at            timestamptz NOT NULL DEFAULT now()
);
CREATE TABLE safety.safety_argument_evidence (   -- GROUNDED_IN
  argument_id  uuid NOT NULL REFERENCES safety.safety_arguments(id),
  evidence_id  uuid NOT NULL REFERENCES safety.evidence(id),
  PRIMARY KEY (argument_id, evidence_id)
);

-- Monitoring — time-series rollup feeding the three lines of assurance
-- (11-safety-case-demonstration-model.md §6; leading/lagging — 08-critical-control-assurance-model.md §5.1)
CREATE TABLE safety.monitoring_summaries (
  id                   uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  critical_control_id  uuid NOT NULL REFERENCES safety.critical_controls(control_id),
  period_start         date NOT NULL,
  period_end           date NOT NULL,
  verification_count   integer NOT NULL DEFAULT 0,
  pass_count           integer NOT NULL DEFAULT 0,
  trend                varchar(20) CHECK (trend IN ('improving','stable','declining')),
  indicator_class      varchar(10) CHECK (indicator_class IN ('leading','lagging')),   -- Guide §11.1
  summary_text         text,
  generated_at         timestamptz NOT NULL DEFAULT now()
);

-- Safety Case Demonstration Engine output (11-safety-case-demonstration-model.md §7)
CREATE TABLE safety.demonstrations (
  id                    uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  demonstration_type    varchar(40) NOT NULL CHECK (demonstration_type IN
                         ('control_adequacy','hazard_to_assurance_chain','moc_effectiveness',
                          'governance_effectiveness','verification_confidence','evidence_support')),
  scope_entity_type     varchar(50) NOT NULL,
  scope_entity_id       uuid NOT NULL,
  generated_narrative   text NOT NULL,
  source_fact_refs      jsonb NOT NULL,
  status                varchar(20) NOT NULL DEFAULT 'draft' CHECK (status IN ('draft','reviewed','approved','published')),
  generated_at          timestamptz NOT NULL DEFAULT now(),
  reviewed_by_person_id uuid REFERENCES safety.persons(id)
);

-- Management of Change (Guide §10.5, §10.12 — 11-safety-case-demonstration-model.md §7.2a)
CREATE TABLE safety.management_of_change (
  id                          uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  asset_id                    uuid REFERENCES safety.assets(id),
  change_description          text NOT NULL,
  change_type                 varchar(10) NOT NULL CHECK (change_type IN ('minor','major')),
  change_category             varchar(30) CHECK (change_category IN
                               ('amusement_device','plant_or_structure','operation_or_nature_of_operation',
                                'worker_safety_role','training','maintenance_or_inspection',
                                'annual_or_major_inspection','organisational')),
  risk_reassessment_required  boolean NOT NULL DEFAULT true,
  linked_safety_assessment_id uuid REFERENCES safety.safety_assessments(id),
  requested_by_person_id      uuid REFERENCES safety.persons(id),
  approved_by_person_id       uuid REFERENCES safety.persons(id),
  status                      varchar(20) NOT NULL DEFAULT 'proposed' CHECK (status IN ('proposed','under_review','approved','implemented','closed')),
  created_at                  timestamptz NOT NULL DEFAULT now(),
  updated_at                  timestamptz NOT NULL DEFAULT now()
);
CREATE TRIGGER trg_moc_updated BEFORE UPDATE ON safety.management_of_change
  FOR EACH ROW EXECUTE FUNCTION set_updated_at();

CREATE TABLE safety.review_triggers (
  id                     uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  trigger_type           varchar(30) NOT NULL CHECK (trigger_type IN
                         ('control_not_controlling_risk','new_adh_identified',
                          'worker_consultation_flagged','regulator_requested','moc_change')),
  moc_id                 uuid REFERENCES safety.management_of_change(id),
  description             text NOT NULL,
  requires_update_of      text[] NOT NULL,   -- subset of {'safety_assessment','emergency_plan','sms','safety_case','competency'}
  status                  varchar(20) NOT NULL DEFAULT 'open' CHECK (status IN ('open','actioned','closed')),
  created_at               timestamptz NOT NULL DEFAULT now()
);

-- SMS Section → Requirement mapping (Schedule 18C-driven — 09-regulatory-knowledge-model.md §5, §7)
CREATE TABLE safety.sms_sections (
  id                uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  name              varchar(100) NOT NULL,
  schedule_18c_ref  varchar(20),
  description       text
);
CREATE TABLE safety.sms_section_requirements (
  sms_section_id  uuid NOT NULL REFERENCES safety.sms_sections(id),
  requirement_id  uuid NOT NULL REFERENCES regulatory.requirements(id),
  PRIMARY KEY (sms_section_id, requirement_id)
);

-- =====================================================================================
-- INCIDENT / ACTION / AUDIT CHAIN — ports incident-report.html, corrective-actions.html,
-- audit-inspection.html near-verbatim (richest, most complete entities in V1)
-- =====================================================================================

CREATE TABLE safety.incidents (
  id                     uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  datetime               timestamptz NOT NULL,
  report_date            date NOT NULL DEFAULT current_date,
  incident_type_concept_id uuid REFERENCES ontology.concepts(id),
  severity               smallint CHECK (severity BETWEEN 1 AND 5),
  vrtp_severity          varchar(30),   -- First Aid | MTI | LTI | Serious Injury | Dangerous Incident | Near Miss
  location               varchar(300),
  asset_id               uuid REFERENCES safety.assets(id),
  reporter_person_id     uuid REFERENCES safety.persons(id),
  description            text NOT NULL,
  injuries               text,
  witnesses              text,
  immediate_actions      text,
  immediate_cause        text,
  root_cause             text,
  whsq_notified          varchar(40) NOT NULL DEFAULT 'Not yet assessed',
  osr_notified           varchar(40) NOT NULL DEFAULT 'Not applicable / under assessment',  -- Chapter 9A
  investigation_status   varchar(20) NOT NULL DEFAULT 'Not Started',
  status                 varchar(20) NOT NULL DEFAULT 'Open',
  created_at             timestamptz NOT NULL DEFAULT now(),
  updated_at             timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX idx_incidents_asset ON safety.incidents(asset_id);
CREATE TRIGGER trg_incidents_updated BEFORE UPDATE ON safety.incidents
  FOR EACH ROW EXECUTE FUNCTION set_updated_at();

CREATE TABLE safety.incident_hazards (
  incident_id uuid NOT NULL REFERENCES safety.incidents(id),
  hazard_id   uuid NOT NULL REFERENCES safety.hazards(id),
  PRIMARY KEY (incident_id, hazard_id)
);

CREATE TABLE safety.investigations (
  id                    uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  incident_id           uuid NOT NULL UNIQUE REFERENCES safety.incidents(id),
  method                varchar(50),      -- TO BE CONFIRMED — ICAM or VRTP-mandated equivalent
  findings              text,
  contributing_factors  text,
  created_at            timestamptz NOT NULL DEFAULT now(),
  updated_at            timestamptz NOT NULL DEFAULT now()
);
CREATE TRIGGER trg_investigations_updated BEFORE UPDATE ON safety.investigations
  FOR EACH ROW EXECUTE FUNCTION set_updated_at();

CREATE TABLE safety.actions (
  id                            uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  source_type_concept_id        uuid REFERENCES ontology.concepts(id),  -- Incident/Audit/Risk Review/Hazard Report/Observation/Other
  source_id                     uuid,   -- polymorphic pointer to the source record
  description                   text NOT NULL,
  root_cause_category_concept_id uuid REFERENCES ontology.concepts(id),
  priority                      varchar(20) CHECK (priority IN ('Critical','High','Medium','Low')),
  assigned_to_person_id         uuid REFERENCES safety.persons(id),
  due_date                      date,
  status                        varchar(20) NOT NULL DEFAULT 'Open' CHECK (status IN ('Open','In Progress','Closed')),
  completion_date               date,
  effectiveness_review          varchar(30) NOT NULL DEFAULT 'Not Reviewed',
  notes                         text,
  created_at                    timestamptz NOT NULL DEFAULT now(),
  updated_at                    timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX idx_actions_due ON safety.actions(due_date);
CREATE TRIGGER trg_actions_updated BEFORE UPDATE ON safety.actions
  FOR EACH ROW EXECUTE FUNCTION set_updated_at();

CREATE TABLE safety.action_controls (   -- REMEDIATES
  action_id  uuid NOT NULL REFERENCES safety.actions(id),
  control_id uuid NOT NULL REFERENCES safety.controls(id),
  PRIMARY KEY (action_id, control_id)
);

CREATE TABLE safety.incident_actions (   -- TRIGGERS
  incident_id uuid NOT NULL REFERENCES safety.incidents(id),
  action_id   uuid NOT NULL REFERENCES safety.actions(id),
  PRIMARY KEY (incident_id, action_id)
);

CREATE TABLE safety.audits (
  id             uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  audit_type     varchar(30) NOT NULL,   -- Internal|External|Site Inspection|Management Review|Regulatory Inspection|Other
  title          varchar(300) NOT NULL,
  scope          text,
  planned_date   date,
  actual_date    date,
  auditor_person_id uuid REFERENCES safety.persons(id),
  area           varchar(300),
  status         varchar(20) NOT NULL DEFAULT 'Planned' CHECK (status IN ('Planned','In Progress','Complete','Cancelled')),
  created_at     timestamptz NOT NULL DEFAULT now(),
  updated_at     timestamptz NOT NULL DEFAULT now()
);
CREATE TRIGGER trg_audits_updated BEFORE UPDATE ON safety.audits
  FOR EACH ROW EXECUTE FUNCTION set_updated_at();

CREATE TABLE safety.audit_findings (
  id          uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  audit_id    uuid NOT NULL REFERENCES safety.audits(id),
  severity    varchar(20),
  description text NOT NULL,
  created_at  timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE safety.audit_finding_actions (   -- TRIGGERS
  finding_id uuid NOT NULL REFERENCES safety.audit_findings(id),
  action_id  uuid NOT NULL REFERENCES safety.actions(id),
  PRIMARY KEY (finding_id, action_id)
);

-- =====================================================================================
-- PROVENANCE SCHEMA — see 05-knowledge-provenance-model.md
-- =====================================================================================

CREATE TYPE provenance.source_type AS ENUM ('document_extraction','human_entry','v1_migration','system_derived');

CREATE TABLE provenance.records (
  id                  uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  entity_type         varchar(50) NOT NULL,   -- 'hazard' | 'control' | 'incident' | ...
  entity_id           uuid NOT NULL,
  source_type         provenance.source_type NOT NULL,
  document_id         uuid REFERENCES safety.documents(id),
  extraction_run_id   uuid,
  created_by_person_id uuid REFERENCES safety.persons(id),
  confidence          numeric(4,3) CHECK (confidence BETWEEN 0 AND 1),
  previous_version_id uuid REFERENCES provenance.records(id),
  created_at          timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX idx_provenance_entity ON provenance.records(entity_type, entity_id);
CREATE INDEX idx_provenance_document ON provenance.records(document_id);

-- =====================================================================================
-- DESIGN BASELINE v1.1 AMENDMENT — Emergency Planning (ACR-002) + Competency Management
-- (ACR-003, supersedes ACR-001). Approved by Architecture Review Board, 2026-08-04.
-- Full assessment: implementation-blueprint/14-architecture-change-requests.md.
-- Sourced from WHSQ Guide §12 (Emergency plans) and §10.8 (Training and competency),
-- read in full 2026-08-04. Reuses existing entities per the review pack's recommendation
-- (credible_events, assets, safety_arguments, evidence) — only genuinely new concepts get
-- new tables here, per the same reuse-over-invent discipline as the rest of this schema.
-- =====================================================================================

-- Emergency Planning (ACR-002). One plan per park (Guide §12.4: "a MAP is regarded as
-- having one amusement device emergency plan"), not per-asset or per-ADI — individual
-- credible events link into it via the join table below.
CREATE TABLE safety.emergency_plans (
  id                          uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  park_id                     uuid NOT NULL UNIQUE REFERENCES safety.parks(id),
  title                       varchar(300) NOT NULL,
  summary                     text NOT NULL,   -- safety-case summary only — Guide §12.4: full plan is not a material particular of the licence
  max_persons_normal_day      integer,         -- Guide §12.4, Schedule 18B 1.3
  max_persons_peak_season     integer,
  warning_system_description  text,            -- Schedule 18B 3.2, 3.4 — workplace warning/communication systems
  corporate_response_plan_description text,    -- Guide §12.1 — corporate emergency response
  status                      varchar(20) NOT NULL DEFAULT 'draft' CHECK (status IN ('draft','current','superseded')),
  effective_date              date,
  sent_to_regulator_at        timestamptz,     -- s.608N(4) — finalised plan sent to consulted emergency service organisations
  created_at                  timestamptz NOT NULL DEFAULT now(),
  updated_at                  timestamptz NOT NULL DEFAULT now()
);
CREATE TRIGGER trg_emergency_plans_updated BEFORE UPDATE ON safety.emergency_plans
  FOR EACH ROW EXECUTE FUNCTION set_updated_at();

-- Links each ADI/credible event into the one park-level plan (Guide §12: "you will need
-- to include linkages from your ADIs to the corresponding amusement device emergency
-- plans"; combining response actions for similar ADIs is expected and must be demonstrable
-- via "a table which links the emergency plans back to the ADIs" — this is that table).
CREATE TABLE safety.emergency_plan_credible_events (
  emergency_plan_id  uuid NOT NULL REFERENCES safety.emergency_plans(id),
  credible_event_id  uuid NOT NULL REFERENCES safety.credible_events(id),
  response_summary   text,   -- the specific response action(s) for this ADI within the combined plan
  PRIMARY KEY (emergency_plan_id, credible_event_id)
);

CREATE TABLE safety.emergency_exercises (
  id                  uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  emergency_plan_id   uuid NOT NULL REFERENCES safety.emergency_plans(id),
  credible_event_id   uuid REFERENCES safety.credible_events(id),   -- nullable: desktop exercises may cover a scenario class, not one specific ADI
  exercise_type       varchar(30) NOT NULL CHECK (exercise_type IN
                       ('drill','scenario_test','desktop_exercise','evacuation_exercise','corporate_response_exercise')),
                       -- Guide §12.1, §12.3 — "more than an evacuation exercise... should involve one of the potential ADI(s)";
                       -- desktop exercises for scenarios impractical to test; a distinct corporate response exercise
  planned_date        date,
  conducted_date      date,
  status              varchar(20) NOT NULL DEFAULT 'planned' CHECK (status IN ('planned','conducted','cancelled')),
  learnings           text,     -- Guide §12: "how you learn from those exercises and how the learnings are assessed and implemented"
  learnings_implemented boolean NOT NULL DEFAULT false,
  created_at          timestamptz NOT NULL DEFAULT now(),
  updated_at          timestamptz NOT NULL DEFAULT now()
);
CREATE TRIGGER trg_emergency_exercises_updated BEFORE UPDATE ON safety.emergency_exercises
  FOR EACH ROW EXECUTE FUNCTION set_updated_at();
CREATE INDEX idx_emergency_exercises_plan ON safety.emergency_exercises(emergency_plan_id);

-- Mandatory consultation with emergency service organisations (Guide §12.2, §12.3;
-- s.608N(2), s.608N(4)) — genuinely new concept, no existing table covers a
-- consultation/recommendation-response pattern (safety_argument_evidence is claim
-- evidence, not this). organisation is a controlled vocabulary, so it is an ontology
-- FK per this file's own governing rule (line 8-11 above), not a free-text/CHECK column.
CREATE TABLE safety.emergency_service_consultations (
  id                        uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  emergency_plan_id         uuid NOT NULL REFERENCES safety.emergency_plans(id),
  organisation_concept_id   uuid REFERENCES ontology.concepts(id),   -- Emergency Service Organisation taxonomy: QFES/QPS/QAS/other
  consultation_date         date,
  recommendation_text       text,
  incorporation_description text,   -- Guide §12.3: "provide information on how those recommendations were incorporated"
  plan_sent_at              timestamptz,   -- s.608N(4)
  created_at                timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX idx_esc_plan ON safety.emergency_service_consultations(emergency_plan_id);

-- Competency Management (ACR-003, supersedes ACR-001 — Training is an evidence_type
-- below, not its own table). Role-based per Guide §10.8's skills-matrix language
-- ("training needs analysis — gap between skills and those required for a role").
CREATE TABLE safety.roles (
  id             uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  name           varchar(200) NOT NULL,
  role_category  varchar(30) CHECK (role_category IN
                 ('operator','technical_services','supervisor','management','officer','contractor','security')),
                 -- Guide §10.8: ride operators, supervisors, senior team members, maintenance staff, contractors,
                 -- security, managers/senior management, and company officers (s.27 WHS Act duty) are all named
  created_at     timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE safety.role_competency_requirements (
  role_id                    uuid NOT NULL REFERENCES safety.roles(id),
  competency_type_concept_id uuid NOT NULL REFERENCES ontology.concepts(id),   -- Competency category taxonomy
  is_mandatory                boolean NOT NULL DEFAULT true,
  PRIMARY KEY (role_id, competency_type_concept_id)
);

-- The claim ("Person X is competent for Role/Control Y"), distinct from the evidence
-- supporting it — mirrors the safety_arguments/safety_argument_evidence split above.
CREATE TABLE safety.competencies (
  id                          uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  person_id                   uuid NOT NULL REFERENCES safety.persons(id),
  role_id                     uuid REFERENCES safety.roles(id),
  critical_control_id         uuid REFERENCES safety.critical_controls(control_id),   -- operator-competency as a control-assurance input
  competency_type_concept_id  uuid REFERENCES ontology.concepts(id),   -- Competency category: training/qualification/licence/oem_certification/authorisation/information_briefing
  description                 text NOT NULL,
  assessed_by_person_id       uuid REFERENCES safety.persons(id),   -- trainer/assessor — Guide §10.8: "management of the trainer's competency and validation of their assessment processes" (self-referential: an assessor's own competency uses this same table)
  assessment_date             date,
  currency_expiry_date        date,    -- refresher/currency — see 07-inference-rules-catalogue.md for the lapse rule (also re-triggered by new ADH/ADI, not time-based alone, per Guide §10.8)
  status                      varchar(20) NOT NULL DEFAULT 'current' CHECK (status IN ('current','lapsed','pending_assessment','revoked')),
  created_at                  timestamptz NOT NULL DEFAULT now(),
  updated_at                  timestamptz NOT NULL DEFAULT now()
);
CREATE TRIGGER trg_competencies_updated BEFORE UPDATE ON safety.competencies
  FOR EACH ROW EXECUTE FUNCTION set_updated_at();
CREATE INDEX idx_competencies_person ON safety.competencies(person_id);
CREATE INDEX idx_competencies_role ON safety.competencies(role_id);
CREATE INDEX idx_competencies_control ON safety.competencies(critical_control_id);

-- Evidence artefact reused as-is (safety.evidence already generic, serving Verification) —
-- competency_type_concept_id on safety.competencies carries the 'training' /
-- 'emergency_response_training' etc. evidence_type distinction; no separate Training table.
CREATE TABLE safety.competency_evidence (   -- mirrors safety_argument_evidence (GROUNDED_IN)
  competency_id  uuid NOT NULL REFERENCES safety.competencies(id),
  evidence_id    uuid NOT NULL REFERENCES safety.evidence(id),
  PRIMARY KEY (competency_id, evidence_id)
);

-- =====================================================================================
-- End of schema. Every table above maps 1:1 to a Neo4j node label in
-- 02-neo4j-node-relationship-model.md; every *_concept_id / source_concept_id column
-- is the FK enforcement point for "no free-text categories" (architecture §1.4 finding 1).
-- =====================================================================================
