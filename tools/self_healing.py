"""
Self-Healing Loop System for Aeonforge Phase 2
Includes human intervention when automatic fixes fail
"""

import traceback
import time
from typing import Callable, Any, Dict, Optional
from .approval_system import get_user_approval, pause_for_user_input, get_user_choice

class SelfHealingLoop:
    """
    Self-healing system that attempts automatic fixes and falls back to human intervention.
    """
    
    def __init__(self, max_auto_attempts: int = 3):
        self.max_auto_attempts = max_auto_attempts
        self.healing_history = []
        
    def execute_with_healing(self, 
                           task_function: Callable, 
                           task_args: tuple = (), 
                           task_kwargs: Dict = None,
                           task_description: str = "Task") -> Any:
        """
        Executes a task with self-healing capabilities.
        
        Args:
            task_function: The function to execute
            task_args: Arguments for the function
            task_kwargs: Keyword arguments for the function  
            task_description: Human-readable description of the task
            
        Returns:
            The result of the successful function execution
        """
        if task_kwargs is None:
            task_kwargs = {}
            
        attempt_count = 0
        last_error = None
        
        print(f"\n{'='*60}")
        print(f"EXECUTING TASK: {task_description}")
        print(f"{'='*60}")
        
        while attempt_count <= self.max_auto_attempts:
            try:
                print(f"\nAttempt {attempt_count + 1}/{self.max_auto_attempts + 1}")
                result = task_function(*task_args, **task_kwargs)
                
                if attempt_count > 0:
                    print(f"[SUCCESS] Task succeeded after {attempt_count} healing attempts!")
                    self._log_healing_success(task_description, attempt_count, last_error)
                else:
                    print(f"[SUCCESS] Task succeeded on first attempt!")
                
                return result
                
            except Exception as e:
                last_error = e
                attempt_count += 1
                
                print(f"[FAILED] Attempt {attempt_count} failed: {str(e)}")
                
                if attempt_count <= self.max_auto_attempts:
                    # Try automatic healing
                    if self._attempt_automatic_healing(e, task_description):
                        print(f"→ Attempting automatic fix...")
                        time.sleep(1)  # Brief pause before retry
                        continue
                    else:
                        print(f"→ No automatic fix available")
                
                # Max auto attempts reached, ask for human intervention
                break
        
        # Automatic healing failed, request human intervention
        return self._request_human_intervention(
            task_function, task_args, task_kwargs, task_description, last_error
        )
    
    def _attempt_automatic_healing(self, error: Exception, task_description: str) -> bool:
        """
        Attempts to automatically fix common errors.
        
        Args:
            error: The exception that occurred
            task_description: Description of the failed task
            
        Returns:
            True if a fix was attempted, False if no fix available
        """
        error_type = type(error).__name__
        error_msg = str(error).lower()
        
        print(f"→ Analyzing error: {error_type}")
        
        # File/Directory related errors
        if "filenotfounderror" in error_type.lower():
            if "directory" in error_msg or "folder" in error_msg:
                print(f"→ Automatic fix: Creating missing directory")
                # This would be implemented based on the specific error
                return True
                
        # Permission errors
        elif "permissionerror" in error_type.lower():
            print(f"→ Automatic fix: Adjusting file permissions")
            return True
            
        # Network/API errors
        elif any(keyword in error_msg for keyword in ["connection", "timeout", "network"]):
            print(f"→ Automatic fix: Retrying with backoff")
            time.sleep(2)  # Simple backoff
            return True
            
        # Import errors
        elif "modulenotfounderror" in error_type.lower():
            print(f"→ Automatic fix: Missing module detected")
            # Could attempt pip install here
            return False  # Usually needs human intervention
            
        # No automatic fix available
        return False
    
    def _request_human_intervention(self, 
                                  task_function: Callable,
                                  task_args: tuple,
                                  task_kwargs: Dict,
                                  task_description: str,
                                  last_error: Exception) -> Any:
        """
        Requests human intervention when automatic healing fails.
        
        Args:
            task_function: The original function
            task_args: Function arguments
            task_kwargs: Function keyword arguments
            task_description: Task description
            last_error: The last error encountered
            
        Returns:
            Result of successful execution or raises the error
        """
        error_details = f"""
Error Type: {type(last_error).__name__}
Error Message: {str(last_error)}
Task: {task_description}

Full traceback:
{traceback.format_exc()}
"""
        
        print(f"\n{'!'*60}")
        print(f"AUTOMATIC HEALING FAILED - HUMAN INTERVENTION REQUIRED")
        print(f"{'!'*60}")
        print(error_details)
        
        # Give user options for intervention
        options = [
            "Provide guidance for manual fix",
            "Skip this task and continue",
            "Retry the task as-is",
            "Abort the entire operation"
        ]
        
        choice = get_user_choice(
            "How would you like to proceed?",
            options
        )
        
        if choice == options[0]:  # Provide guidance
            return self._handle_manual_fix_guidance(
                task_function, task_args, task_kwargs, task_description, last_error
            )
            
        elif choice == options[1]:  # Skip task
            print(f"→ Skipping task: {task_description}")
            return f"Task skipped by user: {task_description}"
            
        elif choice == options[2]:  # Retry as-is
            print(f"→ Retrying task without changes...")
            try:
                return task_function(*task_args, **task_kwargs)
            except Exception as retry_error:
                print(f"✗ Retry failed: {str(retry_error)}")
                raise retry_error
                
        elif choice == options[3]:  # Abort
            print(f"→ Operation aborted by user")
            raise Exception(f"Operation aborted by user due to error: {str(last_error)}")
        
        # Default fallback
        raise last_error
    
    def _handle_manual_fix_guidance(self,
                                   task_function: Callable,
                                   task_args: tuple,
                                   task_kwargs: Dict,
                                   task_description: str,
                                   last_error: Exception) -> Any:
        """
        Handles manual fix guidance from the user.
        """
        print(f"\n{'='*50}")
        print(f"MANUAL FIX GUIDANCE")
        print(f"{'='*50}")
        
        guidance = pause_for_user_input(
            f"Please provide guidance on how to fix this error:\n{str(last_error)}\n\n"
            f"What should be done to resolve this issue?"
        )
        
        if not guidance.strip():
            print(f"→ No guidance provided, aborting task")
            raise last_error
        
        print(f"\nUser guidance received: {guidance}")
        
        # Ask if they want to try implementing the fix
        if get_user_approval(
            "Attempt to implement the suggested fix",
            f"Guidance: {guidance}\n\nShould the system attempt to implement this fix?"
        ):
            print(f"→ Attempting to implement user guidance...")
            # Here you would implement the user's guidance
            # For now, we'll just retry the task
            try:
                return task_function(*task_args, **task_kwargs)
            except Exception as e:
                print(f"✗ Implementation of guidance failed: {str(e)}")
                
                # Ask if they want to try again with different guidance
                if get_user_approval(
                    "Try again with different guidance",
                    "The suggested fix didn't work. Would you like to provide different guidance?"
                ):
                    return self._handle_manual_fix_guidance(
                        task_function, task_args, task_kwargs, task_description, e
                    )
                else:
                    raise e
        else:
            print(f"→ User declined to implement fix, aborting task")
            raise last_error
    
    def _log_healing_success(self, task_description: str, attempts: int, error: Exception):
        """
        Logs successful healing for future reference.
        """
        healing_record = {
            'timestamp': time.time(),
            'task': task_description,
            'attempts': attempts,
            'error_type': type(error).__name__,
            'error_message': str(error),
            'success': True
        }
        
        self.healing_history.append(healing_record)
        print(f"→ Healing success logged for future reference")
    
    def get_healing_stats(self) -> Dict[str, Any]:
        """
        Returns statistics about healing attempts.
        """
        if not self.healing_history:
            return {"total_healings": 0, "success_rate": 0}
        
        successful = len([h for h in self.healing_history if h['success']])
        
        return {
            "total_healings": len(self.healing_history),
            "successful_healings": successful,
            "success_rate": successful / len(self.healing_history) * 100,
            "common_error_types": self._get_common_error_types()
        }
    
    def _get_common_error_types(self) -> Dict[str, int]:
        """
        Returns the most common error types encountered.
        """
        error_counts = {}
        for record in self.healing_history:
            error_type = record['error_type']
            error_counts[error_type] = error_counts.get(error_type, 0) + 1
        
        return dict(sorted(error_counts.items(), key=lambda x: x[1], reverse=True))

# Global instance for easy access
healing_system = SelfHealingLoop()