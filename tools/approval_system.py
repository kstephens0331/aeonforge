"""
Simplified Human-in-the-Loop Approval System for Aeonforge
Implements 1 for approval, 2 for reject system
"""

def get_user_approval(task_description: str, details: str = "") -> bool:
    """
    Gets user approval with simplified 1/2 system.
    
    Args:
        task_description: Brief description of what needs approval
        details: Optional detailed information about the task
        
    Returns:
        True if approved (1), False if rejected (2)
    """
    print(f"\n" + "="*50)
    print(f"APPROVAL REQUIRED")
    print(f"="*50)
    print(f"Task: {task_description}")
    
    if details:
        print(f"\nDetails:")
        print(f"{details}")
    
    print(f"\nOptions:")
    print(f"1 - Approve and continue")
    print(f"2 - Reject and stop")
    
    while True:
        try:
            choice = input(f"\nEnter your choice (1/2): ").strip()
            
            if choice == "1":
                print(f"✓ APPROVED - Proceeding with task...")
                return True
            elif choice == "2":
                print(f"✗ REJECTED - Task cancelled.")
                return False
            else:
                print(f"Invalid choice. Please enter 1 for approve or 2 for reject.")
                
        except (EOFError, KeyboardInterrupt):
            print(f"\n✗ REJECTED - User cancelled.")
            return False

def get_user_choice(question: str, options: list) -> str:
    """
    Gets user choice from a list of options with simplified numbering.
    
    Args:
        question: The question to ask
        options: List of option strings
        
    Returns:
        The selected option string
    """
    print(f"\n" + "="*50)
    print(f"{question}")
    print(f"="*50)
    
    for i, option in enumerate(options, 1):
        print(f"{i} - {option}")
    
    while True:
        try:
            choice = input(f"\nEnter your choice (1-{len(options)}): ").strip()
            
            try:
                choice_num = int(choice)
                if 1 <= choice_num <= len(options):
                    selected_option = options[choice_num - 1]
                    print(f"✓ Selected: {selected_option}")
                    return selected_option
                else:
                    print(f"Invalid choice. Please enter a number between 1 and {len(options)}.")
            except ValueError:
                print(f"Invalid input. Please enter a number between 1 and {len(options)}.")
                
        except (EOFError, KeyboardInterrupt):
            print(f"\n✗ User cancelled.")
            return options[0]  # Return first option as default

def pause_for_user_input(message: str) -> str:
    """
    Pauses execution and gets user input.
    
    Args:
        message: Message to show the user
        
    Returns:
        User's input string
    """
    print(f"\n" + "="*50)
    print(f"USER INPUT REQUIRED")
    print(f"="*50)
    print(f"{message}")
    
    try:
        user_input = input(f"\nYour input: ").strip()
        return user_input
    except (EOFError, KeyboardInterrupt):
        print(f"\n✗ User cancelled.")
        return ""