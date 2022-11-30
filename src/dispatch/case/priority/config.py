default_case_priorities = [
    {
        "name": "Low",
        "description": "This case should be triaged on a best-effort basis.",
        "view_order": 1,
        "color": "#8bc34a",
        "default": True,
        "enabled": True,
    },
    {
        "name": "Medium",
        "description": "This case should be triaged within 24hrs of case creation.",
        "view_order": 2,
        "color": "#ffeb3b",
        "default": False,
        "enabled": True,
    },
    {
        "name": "High",
        "description": "This case should be triaged within 8hrs of case creation.",
        "view_order": 3,
        "color": "#ff9800",
        "default": False,
        "enabled": True,
    },
    {
        "name": "Critical",
        "description": "This case should be triaged immediately.",
        "view_order": 4,
        "color": "#e53935",
        "default": False,
        "enabled": True,
    },
    {
        "name": "Optional",
        "description": "Triage of this case is optional.",
        "view_order": 5,
        "color": "#9e9e9e",
        "default": False,
        "enabled": True,
    },
]
