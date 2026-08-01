from random import choice, randint

severity_map = ['Low', 'Medium', 'High', 'Critical']
priority_map = ['Low', 'Medium', 'High']
category_map = ['UI', 'Backend', 'API', 'Performance', 'Security', 'Infrastructure']
component_map = ['Authentication', 'Database', 'Frontend', 'API Gateway', 'Deployment', 'Notifications']
root_cause_map = [
    'Missing validation on input data',
    'Concurrency issue under load',
    'Incorrect state management',
    'Inefficient database query',
    'Uncaught exception in async workflow',
    'Authentication token mishandled',
]
resolution_map = [
    'Add robust validation and sanitization for user inputs',
    'Refactor the component to use atomic state updates',
    'Optimize query indexes and caching',
    'Add retry logic and error handling around network calls',
    'Implement consistent JWT verification and refresh handling',
]
test_cases_map = [
    'Verify the bug can be reproduced with invalid input',
    'Test the full user flow under peak load',
    'Confirm the response status code and body for edge cases',
    'Validate that all possible states are handled safely',
]

def get_ai_suggestions(description: str) -> dict:
    base = description.strip() or 'The issue description is missing important details.'
    enhanced = f"{base.strip().capitalize()} This issue affects user workflows and should be prioritized with clear steps to reproduce."
    return {
        'enhanced_description': enhanced,
        'severity': choice(severity_map),
        'priority': choice(priority_map),
        'category': choice(category_map),
        'component': choice(component_map),
        'root_cause': choice(root_cause_map),
        'resolution': choice(resolution_map),
        'test_cases': choice(test_cases_map),
        'estimated_time': f"{randint(1, 5)} days",
        'confidence': f"{randint(80, 99)}%",
    }
