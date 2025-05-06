import pytest
from typing import List, Dict, Any
from prometheus_swarm.database.models import Evidence
from prometheus_swarm.database.database import get_db_session

def test_evidence_uniqueness_integration():
    """
    Integration test to verify evidence uniqueness in the database.
    
    This test ensures that:
    1. Multiple pieces of evidence with the same key attributes 
       cannot be inserted into the database
    2. Unique constraints are properly enforced
    """
    # Setup database session
    session = get_db_session()
    
    try:
        # Create initial evidence with unique attributes
        initial_evidence = Evidence(
            source_repo='test-repo',
            source_url='https://github.com/test/repo',
            evidence_type='integration-test',
            content='Unique test evidence'
        )
        session.add(initial_evidence)
        session.commit()
        
        # Attempt to insert duplicate evidence
        duplicate_evidence = Evidence(
            source_repo='test-repo',
            source_url='https://github.com/test/repo',
            evidence_type='integration-test',
            content='Duplicate test evidence'
        )
        
        # Check that inserting a duplicate raises an integrity error
        with pytest.raises(Exception) as excinfo:
            session.add(duplicate_evidence)
            session.commit()
        
        assert 'UNIQUE constraint' in str(excinfo.value)
    
    finally:
        # Cleanup: remove test evidence
        session.query(Evidence).filter_by(
            source_repo='test-repo', 
            evidence_type='integration-test'
        ).delete()
        session.commit()

def test_evidence_uniqueness_constraints():
    """
    Test the uniqueness constraints for Evidence model.
    
    Verifies that evidence entries are unique based on:
    - source_repo
    - source_url
    - evidence_type
    """
    session = get_db_session()
    
    try:
        # Create evidence scenarios
        evidence_scenarios = [
            # Completely unique
            Evidence(
                source_repo='repo1',
                source_url='https://github.com/test1/repo',
                evidence_type='type1',
                content='Evidence 1'
            ),
            # Different repo
            Evidence(
                source_repo='repo2',
                source_url='https://github.com/test1/repo',
                evidence_type='type1',
                content='Evidence 2'
            ),
            # Different URL
            Evidence(
                source_repo='repo1',
                source_url='https://github.com/test2/repo',
                evidence_type='type1',
                content='Evidence 3'
            ),
            # Different type
            Evidence(
                source_repo='repo1',
                source_url='https://github.com/test1/repo',
                evidence_type='type2',
                content='Evidence 4'
            )
        ]
        
        # Add all unique evidence
        for evidence in evidence_scenarios:
            session.add(evidence)
        session.commit()
        
        # Verify all unique evidence can be added
        assert len(session.query(Evidence).filter(
            Evidence.source_repo.in_(['repo1', 'repo2']),
            Evidence.evidence_type.in_(['type1', 'type2'])
        ).all()) == 4
        
        # Attempt to insert a duplicate (exactly same attributes)
        with pytest.raises(Exception) as excinfo:
            duplicate_evidence = Evidence(
                source_repo='repo1',
                source_url='https://github.com/test1/repo',
                evidence_type='type1',
                content='Duplicate Evidence'
            )
            session.add(duplicate_evidence)
            session.commit()
        
        assert 'UNIQUE constraint' in str(excinfo.value)
    
    finally:
        # Cleanup: remove test evidence
        session.query(Evidence).filter(
            Evidence.source_repo.in_(['repo1', 'repo2']),
            Evidence.evidence_type.in_(['type1', 'type2'])
        ).delete()
        session.commit()

def test_evidence_e2e_workflow():
    """
    End-to-end test for evidence creation, retrieval, and uniqueness.
    
    Simulates a complete workflow of creating and managing evidence.
    """
    session = get_db_session()
    
    try:
        # Create initial evidence
        initial_evidence = Evidence(
            source_repo='workflow-test-repo',
            source_url='https://github.com/workflow/test-repo',
            evidence_type='e2e-workflow',
            content='Initial workflow evidence'
        )
        session.add(initial_evidence)
        session.commit()
        
        # Retrieve the evidence
        retrieved_evidence = session.query(Evidence).filter_by(
            source_repo='workflow-test-repo',
            evidence_type='e2e-workflow'
        ).first()
        
        assert retrieved_evidence is not None
        assert retrieved_evidence.content == 'Initial workflow evidence'
        
        # Verify uniqueness by attempting duplicate insertion
        with pytest.raises(Exception) as excinfo:
            duplicate_evidence = Evidence(
                source_repo='workflow-test-repo',
                source_url='https://github.com/workflow/test-repo',
                evidence_type='e2e-workflow',
                content='Duplicate workflow evidence'
            )
            session.add(duplicate_evidence)
            session.commit()
        
        assert 'UNIQUE constraint' in str(excinfo.value)
    
    finally:
        # Cleanup: remove test evidence
        session.query(Evidence).filter_by(
            source_repo='workflow-test-repo',
            evidence_type='e2e-workflow'
        ).delete()
        session.commit()