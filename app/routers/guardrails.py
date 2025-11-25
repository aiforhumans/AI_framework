"""
Guardrails Router.

Handles safety testing and content moderation:
- Rule management (PII, keyword, regex, content filters)
- Test case management
- Real-time guardrail checking
- Test suite execution
"""

from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from typing import List, Optional

from app.schemas.requests import (
    GuardrailRuleCreateRequest, GuardrailRuleUpdateRequest,
    GuardrailTestCreateRequest, GuardrailTestUpdateRequest,
    GuardrailCheckRequest,
)
from app.routers import get_service

router = APIRouter(prefix="/api/guardrails", tags=["Guardrails"])


# =============================================================================
# GUARDRAIL RULES
# =============================================================================

@router.get("/rules", response_class=JSONResponse)
async def list_guardrail_rules():
    """List all guardrail rules."""
    rules = get_service().list_guardrail_rules()
    return {"rules": [r.model_dump() for r in rules]}


@router.get("/rules/{rule_id}", response_class=JSONResponse)
async def get_guardrail_rule(rule_id: int):
    """Get a specific guardrail rule."""
    rule = get_service().get_guardrail_rule(rule_id)
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")
    return rule.model_dump()


@router.post("/rules", response_class=JSONResponse)
async def create_guardrail_rule(payload: GuardrailRuleCreateRequest):
    """Create a new guardrail rule (pii, keyword, regex, content, llm)."""
    return get_service().create_guardrail_rule(payload).model_dump()


@router.put("/rules/{rule_id}", response_class=JSONResponse)
async def update_guardrail_rule(rule_id: int, payload: GuardrailRuleUpdateRequest):
    """Update a guardrail rule."""
    result = get_service().update_guardrail_rule(rule_id, payload)
    if not result:
        raise HTTPException(status_code=404, detail="Rule not found")
    return result.model_dump()


@router.delete("/rules/{rule_id}", response_class=JSONResponse)
async def delete_guardrail_rule(rule_id: int):
    """Delete a guardrail rule."""
    if not get_service().delete_guardrail_rule(rule_id):
        raise HTTPException(status_code=404, detail="Rule not found")
    return {"success": True}


@router.post("/rules/{rule_id}/toggle", response_class=JSONResponse)
async def toggle_guardrail_rule(rule_id: int):
    """Toggle a guardrail rule's enabled status."""
    result = get_service().toggle_guardrail_rule(rule_id)
    if not result:
        raise HTTPException(status_code=404, detail="Rule not found")
    return result.model_dump()


# =============================================================================
# GUARDRAIL TEST CASES
# =============================================================================

@router.get("/tests", response_class=JSONResponse)
async def list_guardrail_tests():
    """List all guardrail test cases."""
    tests = get_service().list_guardrail_tests()
    return {"tests": [t.model_dump() for t in tests]}


@router.get("/tests/{test_id}", response_class=JSONResponse)
async def get_guardrail_test(test_id: int):
    """Get a specific guardrail test case."""
    test = get_service().get_guardrail_test(test_id)
    if not test:
        raise HTTPException(status_code=404, detail="Test not found")
    return test.model_dump()


@router.post("/tests", response_class=JSONResponse)
async def create_guardrail_test(payload: GuardrailTestCreateRequest):
    """Create a guardrail test case with expected outcomes."""
    return get_service().create_guardrail_test(payload).model_dump()


@router.put("/tests/{test_id}", response_class=JSONResponse)
async def update_guardrail_test(test_id: int, payload: GuardrailTestUpdateRequest):
    """Update a guardrail test case."""
    result = get_service().update_guardrail_test(test_id, payload)
    if not result:
        raise HTTPException(status_code=404, detail="Test not found")
    return result.model_dump()


@router.delete("/tests/{test_id}", response_class=JSONResponse)
async def delete_guardrail_test(test_id: int):
    """Delete a guardrail test case."""
    if not get_service().delete_guardrail_test(test_id):
        raise HTTPException(status_code=404, detail="Test not found")
    return {"success": True}


# =============================================================================
# GUARDRAIL EXECUTION
# =============================================================================

@router.post("/check", response_class=JSONResponse)
async def check_guardrails(payload: GuardrailCheckRequest):
    """Run guardrail checks on input text."""
    result = get_service().check_guardrails(payload)
    return result.model_dump()


@router.post("/run-tests", response_class=JSONResponse)
async def run_guardrail_test_suite(rule_ids: str = None, test_ids: str = None):
    """
    Run guardrail test suite.
    
    Returns pass/fail status for each test case against enabled rules.
    """
    rule_id_list = [int(x) for x in rule_ids.split(",")] if rule_ids else None
    test_id_list = [int(x) for x in test_ids.split(",")] if test_ids else None
    return get_service().run_guardrail_test_suite(rule_id_list, test_id_list)
