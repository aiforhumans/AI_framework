from __future__ import annotations

from pathlib import Path
from typing import List, Optional

from pydantic import BaseModel, Field


DATA_FILE = Path("app/data/prompt_templates.json")


class PromptTemplate(BaseModel):
    id: int = Field(..., description="Unique template identifier")
    name: str
    description: str = ""
    category: str = "custom"  # "custom", "roleplay", "cot", "fewshot", "structured"
    system_prompt: str = ""
    user_prompt: str = ""
    variables: list[str] = Field(default_factory=list)
    is_preset: bool = False  # True for built-in templates


# Pre-built template modes
PRESET_TEMPLATES = [
    # Chain-of-Thought Templates
    PromptTemplate(
        id=-1,
        name="Chain of Thought",
        description="Step-by-step reasoning for complex problems",
        category="cot",
        system_prompt="""You are a helpful assistant that thinks through problems step by step.

For each question:
1. Break down the problem into smaller parts
2. Think through each part carefully
3. Show your reasoning at each step
4. Arrive at a final answer

Always format your response as:
**Thinking:**
[Your step-by-step reasoning]

**Answer:**
[Your final answer]""",
        user_prompt="{{question}}",
        variables=["question"],
        is_preset=True,
    ),
    PromptTemplate(
        id=-2,
        name="Think Step by Step",
        description="Simple CoT prompting",
        category="cot",
        system_prompt="You are a logical problem solver. When answering, think step by step and explain your reasoning clearly before giving your final answer.",
        user_prompt="{{question}}\n\nLet's think through this step by step:",
        variables=["question"],
        is_preset=True,
    ),
    PromptTemplate(
        id=-3,
        name="Self-Consistency CoT",
        description="Multiple reasoning paths for robust answers",
        category="cot",
        system_prompt="""You are an expert problem solver. For this problem:
1. Generate 3 different approaches to solve it
2. Work through each approach step by step
3. Compare the results
4. Provide the most consistent answer

Format:
**Approach 1:** [reasoning]
**Approach 2:** [reasoning]  
**Approach 3:** [reasoning]
**Comparison:** [analysis]
**Final Answer:** [answer]""",
        user_prompt="{{question}}",
        variables=["question"],
        is_preset=True,
    ),
    
    # Few-Shot Templates
    PromptTemplate(
        id=-4,
        name="Few-Shot Classification",
        description="Learn from examples to classify text",
        category="fewshot",
        system_prompt="You are a text classifier. Learn from the examples provided and classify the new text.",
        user_prompt="""Here are some examples:

{{examples}}

Now classify this text:
Text: {{text}}
Classification:""",
        variables=["examples", "text"],
        is_preset=True,
    ),
    PromptTemplate(
        id=-5,
        name="Few-Shot Q&A",
        description="Answer questions based on example format",
        category="fewshot",
        system_prompt="You are a helpful assistant. Follow the format shown in the examples to answer the question.",
        user_prompt="""Examples:
{{examples}}

Question: {{question}}
Answer:""",
        variables=["examples", "question"],
        is_preset=True,
    ),
    PromptTemplate(
        id=-6,
        name="Few-Shot Translation",
        description="Translate following example patterns",
        category="fewshot",
        system_prompt="You are a translator. Follow the translation pattern shown in the examples.",
        user_prompt="""Translation examples ({{source_lang}} to {{target_lang}}):
{{examples}}

Translate this:
{{source_lang}}: {{text}}
{{target_lang}}:""",
        variables=["source_lang", "target_lang", "examples", "text"],
        is_preset=True,
    ),
    
    # Role-Play Templates
    PromptTemplate(
        id=-7,
        name="Expert Persona",
        description="Assume the role of a domain expert",
        category="roleplay",
        system_prompt="""You are {{expert_name}}, a world-renowned expert in {{domain}} with {{years}} years of experience.

Your expertise includes:
{{expertise_areas}}

You communicate in a {{tone}} manner, using appropriate technical terminology while remaining accessible. Draw on your extensive experience to provide detailed, authoritative answers.""",
        user_prompt="{{question}}",
        variables=["expert_name", "domain", "years", "expertise_areas", "tone", "question"],
        is_preset=True,
    ),
    PromptTemplate(
        id=-8,
        name="Socratic Teacher",
        description="Guide through questioning instead of direct answers",
        category="roleplay",
        system_prompt="""You are a Socratic teacher. Instead of giving direct answers:
1. Ask clarifying questions to understand the student's current knowledge
2. Guide them with probing questions that lead to insights
3. Encourage critical thinking and self-discovery
4. Provide hints when they're stuck, but let them reach conclusions themselves

Always be patient, encouraging, and focus on developing understanding rather than just providing answers.""",
        user_prompt="Student's question: {{question}}",
        variables=["question"],
        is_preset=True,
    ),
    PromptTemplate(
        id=-9,
        name="Devil's Advocate",
        description="Challenge ideas and find counterarguments",
        category="roleplay",
        system_prompt="""You are a critical thinker playing devil's advocate. Your role is to:
1. Challenge assumptions in the given argument
2. Find potential weaknesses and counterarguments
3. Identify logical fallacies or gaps in reasoning
4. Present alternative perspectives
5. Be respectful but thorough in your critique

Always explain your counterarguments clearly and suggest how the argument could be strengthened.""",
        user_prompt="Please challenge this argument:\n\n{{argument}}",
        variables=["argument"],
        is_preset=True,
    ),
    PromptTemplate(
        id=-10,
        name="Interview Simulator",
        description="Practice technical or behavioral interviews",
        category="roleplay",
        system_prompt="""You are an experienced {{interview_type}} interviewer at a {{company_type}} company. 

Your role:
1. Ask relevant, challenging interview questions
2. Follow up based on candidate responses
3. Provide constructive feedback after each answer
4. Score responses on a 1-5 scale with explanations
5. Give tips for improvement

Be professional, realistic, and helpful in preparing the candidate for real interviews.""",
        user_prompt="Start the interview for a {{position}} position. Topic focus: {{topic}}",
        variables=["interview_type", "company_type", "position", "topic"],
        is_preset=True,
    ),
    
    # Structured Output Templates
    PromptTemplate(
        id=-11,
        name="JSON Output",
        description="Generate structured JSON responses",
        category="structured",
        system_prompt="""You are a data extraction assistant. Extract information from the input and format it as valid JSON.

Output schema:
{{schema}}

Rules:
- Always output valid JSON
- Use null for missing values
- Follow the exact schema structure
- Do not include any text outside the JSON object""",
        user_prompt="Extract information from:\n{{input}}",
        variables=["schema", "input"],
        is_preset=True,
    ),
    PromptTemplate(
        id=-12,
        name="Markdown Report",
        description="Generate structured markdown reports",
        category="structured",
        system_prompt="""You are a report generator. Create well-structured markdown reports with:
- Clear headings (H1, H2, H3)
- Bullet points for lists
- Tables where appropriate
- Code blocks for technical content
- Bold/italic for emphasis

Follow the report template:
{{template}}""",
        user_prompt="Generate a report on: {{topic}}\n\nDetails: {{details}}",
        variables=["template", "topic", "details"],
        is_preset=True,
    ),
    PromptTemplate(
        id=-13,
        name="Code Review",
        description="Structured code review feedback",
        category="structured",
        system_prompt="""You are a senior code reviewer. Analyze code and provide structured feedback:

## Summary
[Brief overview of the code]

## Issues Found
- 🔴 Critical: [blocking issues]
- 🟡 Warning: [should fix]
- 🟢 Suggestion: [nice to have]

## Security Concerns
[Any security issues]

## Performance Notes
[Any performance concerns]

## Code Quality
- Readability: [score/10]
- Maintainability: [score/10]
- Best Practices: [score/10]

## Recommendations
[Specific improvement suggestions]""",
        user_prompt="Review this {{language}} code:\n\n```{{language}}\n{{code}}\n```",
        variables=["language", "code"],
        is_preset=True,
    ),
    PromptTemplate(
        id=-14,
        name="Pros and Cons Analysis",
        description="Balanced analysis with structured output",
        category="structured",
        system_prompt="""You are an objective analyst. Provide balanced analysis in this format:

## Topic: [topic]

### Pros ✅
1. [advantage]
2. [advantage]
...

### Cons ❌
1. [disadvantage]
2. [disadvantage]
...

### Key Considerations
- [important factor]
...

### Recommendation
[Your balanced recommendation based on the analysis]""",
        user_prompt="Analyze: {{topic}}\n\nContext: {{context}}",
        variables=["topic", "context"],
        is_preset=True,
    ),
]


class PromptTemplateStore:
    def __init__(self, data_file: Path | None = None) -> None:
        self.data_file = data_file or DATA_FILE
        if not self.data_file.parent.exists():
            self.data_file.parent.mkdir(parents=True, exist_ok=True)
        if not self.data_file.exists():
            self._write_all([])

    def _read_all(self) -> List[PromptTemplate]:
        import json

        if not self.data_file.exists():
            return []
        with self.data_file.open("r", encoding="utf-8") as f:
            raw = json.load(f) or []
        return [PromptTemplate(**item) for item in raw]

    def _write_all(self, templates: List[PromptTemplate]) -> None:
        import json

        with self.data_file.open("w", encoding="utf-8") as f:
            json.dump([t.model_dump() for t in templates], f, indent=2)

    def list_templates(self, include_presets: bool = True) -> List[PromptTemplate]:
        """List all templates, optionally including presets."""
        custom = self._read_all()
        if include_presets:
            return PRESET_TEMPLATES + custom
        return custom

    def list_presets(self) -> List[PromptTemplate]:
        """List only preset templates."""
        return PRESET_TEMPLATES

    def list_by_category(self, category: str) -> List[PromptTemplate]:
        """List templates by category."""
        all_templates = self.list_templates()
        return [t for t in all_templates if t.category == category]

    def get_template(self, template_id: int) -> Optional[PromptTemplate]:
        # Check presets first (negative IDs)
        if template_id < 0:
            for t in PRESET_TEMPLATES:
                if t.id == template_id:
                    return t
            return None
        # Check custom templates
        for t in self._read_all():
            if t.id == template_id:
                return t
        return None

    def _next_id(self, templates: List[PromptTemplate]) -> int:
        if not templates:
            return 1
        return max(t.id for t in templates) + 1

    def create_template(self, template: PromptTemplate) -> PromptTemplate:
        templates = self._read_all()
        template.id = self._next_id(templates)
        templates.append(template)
        self._write_all(templates)
        return template

    def update_template(self, template_id: int, update: dict) -> Optional[PromptTemplate]:
        templates = self._read_all()
        updated: Optional[PromptTemplate] = None
        for idx, t in enumerate(templates):
            if t.id == template_id:
                data = t.model_dump()
                data.update(update)
                updated = PromptTemplate(**data)
                templates[idx] = updated
                break
        if updated is not None:
            self._write_all(templates)
        return updated

    def delete_template(self, template_id: int) -> bool:
        templates = self._read_all()
        new_templates = [t for t in templates if t.id != template_id]
        if len(new_templates) == len(templates):
            return False
        self._write_all(new_templates)
        return True
