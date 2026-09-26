"""F04: bind the accepted artifact to its VALIDATED proof (independent-review R1, R2)

Revision ID: e7c1d4a9b206
Revises: c2e7b9a4f513
Create Date: 2026-09-25 00:00:03.000000

Independent backend review, FBR-F04-R1 and FBR-F04-R2. Both sit on the one
relation pre-implementation binding PI-1 defines: the accepted effect must
provably BE the VALIDATED candidate and its persisted proof (06 §16 home
note; 09 §118 "output fingerprint" + "AI_VALIDATION_PROOF reference",
mandatory for high-assurance use).

R1 (BEFORE INSERT, immediate): an accepted `ai_derived_artifacts` row
(`session_id` set) is refused unless
- a VALIDATED `ai_validation_proofs` row of the same generation and operation
  exists; the acceptance commit inserts the proof before the artifact; and
- `sha256(content) = content_fingerprint = proof.output_fingerprint`, i.e. the
  content is the exact bytes the validator fingerprinted, not a re-serialization.

R2 (DEFERRABLE INITIALLY DEFERRED constraint triggers, checked at COMMIT):
- a VALIDATED proof requires its generation to be VALIDATED with an accepted
  artifact;
- an F04 generation (`session_id` set) that becomes VALIDATED requires its
  VALIDATED proof and accepted artifact.
Together with R1 this is PI-1 at persistence: a VALIDATED proof exists iff its
generation is VALIDATED and has exactly one accepted artifact (uniqueness per
generation already exists), all in one commit. REJECTED / INDETERMINATE proofs
and pre-F04 generations (`session_id` NULL) are untouched.

Rows written before this revision are not rewritten (the tables are
append-only). The pre-repair runtime database was recreated instead; see the F04
evidence.
"""

from __future__ import annotations

from alembic import op

revision = "e7c1d4a9b206"
down_revision = "c2e7b9a4f513"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        CREATE FUNCTION trg_ai_derived_artifacts_validated_binding() RETURNS trigger AS $$
        DECLARE
            proof ai_validation_proofs%ROWTYPE;
        BEGIN
            SELECT * INTO proof FROM ai_validation_proofs
                WHERE ai_generation_id = NEW.ai_generation_id;
            IF proof.id IS NULL
                OR proof.validation_result <> 'VALIDATED'
                OR proof.ai_operation_id <> NEW.ai_operation_id
                OR proof.output_fingerprint <> NEW.content_fingerprint
                OR NEW.content_fingerprint
                    <> encode(sha256(convert_to(NEW.content, 'UTF8')), 'hex')
            THEN
                RAISE EXCEPTION
                    'accepted artifact must be the validated output: a VALIDATED proof of the '
                    'same generation and operation whose output_fingerprint = content_fingerprint '
                    '= sha256(content) (F04 PI-1, 09 §118)';
            END IF;
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
        """
    )
    op.execute(
        """
        CREATE TRIGGER trg_ai_derived_artifacts_validated_binding
        BEFORE INSERT ON ai_derived_artifacts
        FOR EACH ROW WHEN (NEW.session_id IS NOT NULL)
        EXECUTE FUNCTION trg_ai_derived_artifacts_validated_binding();
        """
    )
    op.execute(
        """
        CREATE FUNCTION trg_ai_validation_proofs_pi1_bundle() RETURNS trigger AS $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM ai_generations g
                JOIN ai_derived_artifacts a
                  ON a.ai_generation_id = g.id AND a.session_id IS NOT NULL
                WHERE g.id = NEW.ai_generation_id AND g.status = 'VALIDATED'
            ) THEN
                RAISE EXCEPTION
                    'a VALIDATED proof requires its VALIDATED generation and accepted artifact '
                    'in the same commit (F04 PI-1)';
            END IF;
            RETURN NULL;
        END;
        $$ LANGUAGE plpgsql;
        """
    )
    op.execute(
        """
        CREATE CONSTRAINT TRIGGER trg_ai_validation_proofs_pi1_bundle
        AFTER INSERT ON ai_validation_proofs
        DEFERRABLE INITIALLY DEFERRED
        FOR EACH ROW WHEN (NEW.validation_result = 'VALIDATED')
        EXECUTE FUNCTION trg_ai_validation_proofs_pi1_bundle();
        """
    )
    op.execute(
        """
        CREATE FUNCTION trg_ai_generations_pi1_bundle() RETURNS trigger AS $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM ai_validation_proofs p
                JOIN ai_derived_artifacts a
                  ON a.ai_generation_id = p.ai_generation_id AND a.session_id IS NOT NULL
                WHERE p.ai_generation_id = NEW.id AND p.validation_result = 'VALIDATED'
            ) THEN
                RAISE EXCEPTION
                    'a VALIDATED F04 generation requires its VALIDATED proof and accepted '
                    'artifact in the same commit (F04 PI-1)';
            END IF;
            RETURN NULL;
        END;
        $$ LANGUAGE plpgsql;
        """
    )
    op.execute(
        """
        CREATE CONSTRAINT TRIGGER trg_ai_generations_pi1_bundle
        AFTER UPDATE ON ai_generations
        DEFERRABLE INITIALLY DEFERRED
        FOR EACH ROW WHEN (NEW.status = 'VALIDATED' AND NEW.session_id IS NOT NULL)
        EXECUTE FUNCTION trg_ai_generations_pi1_bundle();
        """
    )


def downgrade() -> None:
    op.execute("DROP TRIGGER IF EXISTS trg_ai_generations_pi1_bundle ON ai_generations;")
    op.execute("DROP FUNCTION IF EXISTS trg_ai_generations_pi1_bundle();")
    op.execute("DROP TRIGGER IF EXISTS trg_ai_validation_proofs_pi1_bundle ON ai_validation_proofs;")
    op.execute("DROP FUNCTION IF EXISTS trg_ai_validation_proofs_pi1_bundle();")
    op.execute(
        "DROP TRIGGER IF EXISTS trg_ai_derived_artifacts_validated_binding ON ai_derived_artifacts;"
    )
    op.execute("DROP FUNCTION IF EXISTS trg_ai_derived_artifacts_validated_binding();")
