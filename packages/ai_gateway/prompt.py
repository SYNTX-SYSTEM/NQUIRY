"""InvocationPrompt: modular, versioned prompt assembly with structural
DATA delimitation.

Source: 08_AI_ARCHITECTURE_AND_CONTRACTS.md section 8 (Prompt
Architecture -- "Do not store one enormous system prompt. Use modular
prompt templates." -- closed as "AI Operation Contract + Prompt
Template Version + Mode Template + Bounded Context + Tool Declaration
where allowed = Invocation Prompt"), section 8.1 (Prompt Version --
"Every consequentially relevant AI output must be traceable to the
prompt/contract version used"), section 8.2 (Prompt Is Not Authority --
"A prompt instruction such as 'approve'/'select'/'execute'/'persist'
cannot create an authority path. The surrounding System boundaries
still decide what may happen."), section 9 (Prompt Injection and
Retrieved-Content Instruction Boundary -- "[ARCHITECTURAL CLOSURE].
User content, imported content, Evidence, research sources and
retrieved text are treated as: DATA... Instructions embedded in
retrieved/user content may not: change operation contract, change
authority class, change Workspace scope, grant tool access, override
boundary DENY, disable provenance, change model routing policy, cause
direct persistence. Retrieved content cannot promote itself into
System instruction.").

WHY `system_instructions` AND `data_blocks` ARE SEPARATE, DISTINCTLY-
TYPED FIELDS -- NOT ONE CONCATENATED STRING
--------------------------------------------------------------------
This is the structural half of 08 section 9's own boundary: an
`InvocationPrompt` cannot even REPRESENT "the model's entire input as
one opaque string" -- system instructions and bounded context/data are
two different collections on this type. Whatever a `DataBlock`'s own
`content` contains, there is no code path anywhere in this module (or
in `ai_gateway.gateway`/`ai_gateway.adapters.providers.mock`) that
reads a `DataBlock.content` string and reinterprets it as a new
`system_instructions` entry, a different `ai_operation_id`, or a
boundary verdict. `MockProviderAdapter`'s own deterministic response
(see that module) is a function of the OPERATION and an explicit
scripted outcome, never of `DataBlock.content` -- proven directly by
`tests/ai/test_prompt.py`'s own adversarial case: a data block
containing literal instruction-shaped text produces byte-identical
`InvocationPrompt` structure to a benign control, and downstream
behavior is provably unaffected.

WHY THIS MODULE HOLDS NO "SANITIZATION"/"STRIPPING" LOGIC
--------------------------------------------------------------------
08 section 9 does not ask retrieved content to be rewritten or
filtered -- it asks that embedded instructions never be PROMOTED into
system instruction. Attempting to detect and strip "instruction-like"
phrases would be an unbounded, guessable filter (and itself a form of
semantic invention 14 forbids: inventing a detection policy 08 never
specifies). The actual, provable defense is structural non-promotion:
DATA stays in the DATA collection, full stop -- proven by type shape,
not by pattern-matching content.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass

from ai_contracts.aiop import AIOperationId
from semantic_types.versions import ContractVersion, PromptVersion


@dataclass(frozen=True, slots=True)
class DataBlock:
    """One unit of bounded context, always treated as DATA (08 section
    9) -- never as an instruction, regardless of its own content."""

    source_ref: str
    content: str

    def __post_init__(self) -> None:
        if not self.source_ref:
            raise ValueError("DataBlock.source_ref must be non-empty")

    @property
    def content_fingerprint(self) -> str:
        return hashlib.sha256(self.content.encode("utf-8")).hexdigest()


@dataclass(frozen=True, slots=True)
class InvocationPrompt:
    """08 section 8's own closure: AI Operation Contract + Prompt
    Template Version + Mode Template + Bounded Context (+ Tool
    Declaration, NOT_APPLICABLE -- 14 PKG-19's own scope has no tool
    access, see `21_TOOL_ACCESS_ARCHITECTURE` in 08, unused here)."""

    ai_operation_id: AIOperationId
    ai_operation_contract_version: ContractVersion
    prompt_version: PromptVersion
    mode_template_ref: str
    system_instructions: str
    data_blocks: tuple[DataBlock, ...]

    def __post_init__(self) -> None:
        if not isinstance(self.ai_operation_id, AIOperationId):
            raise TypeError(
                f"ai_operation_id must be an AIOperationId, got {type(self.ai_operation_id)!r}"
            )
        if not isinstance(self.ai_operation_contract_version, ContractVersion):
            raise TypeError(
                "ai_operation_contract_version must be a ContractVersion, got "
                f"{type(self.ai_operation_contract_version)!r}"
            )
        if not isinstance(self.prompt_version, PromptVersion):
            raise TypeError(
                f"prompt_version must be a PromptVersion, got {type(self.prompt_version)!r}"
            )
        if not self.mode_template_ref:
            raise ValueError("InvocationPrompt.mode_template_ref must be non-empty")
        if not self.system_instructions:
            raise ValueError("InvocationPrompt.system_instructions must be non-empty")

    def render_delimited_text(self) -> str:
        """A textual rendering for audit/logging/mock-consumption only
        -- NOT the channel any boundary or acceptance decision reads.
        Each data block is wrapped with a delimiter naming its own
        content fingerprint, so a block cannot forge a closing
        delimiter that collides with a DIFFERENT block's own fingerprint
        without detection; this is a legibility aid, not the actual
        DATA/instruction separation itself (that separation is
        structural -- see module docstring)."""
        rendered_blocks = "\n".join(
            f'<DATA source="{block.source_ref}" fingerprint="{block.content_fingerprint}">'
            f"{block.content}"
            f"</DATA>"
            for block in self.data_blocks
        )
        return f"{self.system_instructions}\n{rendered_blocks}"


def build_invocation_prompt(
    *,
    ai_operation_id: AIOperationId,
    ai_operation_contract_version: ContractVersion,
    prompt_version: PromptVersion,
    mode_template_ref: str,
    system_instructions: str,
    data_blocks: tuple[DataBlock, ...],
) -> InvocationPrompt:
    return InvocationPrompt(
        ai_operation_id=ai_operation_id,
        ai_operation_contract_version=ai_operation_contract_version,
        prompt_version=prompt_version,
        mode_template_ref=mode_template_ref,
        system_instructions=system_instructions,
        data_blocks=data_blocks,
    )


__all__ = ["DataBlock", "InvocationPrompt", "build_invocation_prompt"]
