"""
Simple CLI Agent with Gemini + Code Execution (E2B or VM)
"""
import asyncio
import re
import sys
import vertexai
from vertexai.generative_models import GenerativeModel, GenerationConfig
from code_executor import CodeExecutor
from vm_executor import VMExecutor
import config


def extract_code_blocks(text: str) -> list:
    """
    Extract Python code blocks from markdown text
    
    Args:
        text: Markdown text containing code blocks
        
    Returns:
        List of code strings
    """
    # Match ```python or ``` blocks
    patterns = [
        r'```python\n(.*?)```',
        r'```\n(.*?)```'
    ]
    
    code_blocks = []
    for pattern in patterns:
        matches = re.findall(pattern, text, re.DOTALL)
        code_blocks.extend(matches)
    
    return code_blocks


async def main():
    """Main CLI application loop"""
    
    print("\n" + "="*70)
    print("GEMINI + CODE EXECUTION AGENT")
    print("="*70)
    
    # Get GCP project ID
    project_id = config.GCP_PROJECT_ID
    if not project_id:
        project_id = input("\nEnter your GCP Project ID: ").strip()
        if not project_id:
            print("Error: Project ID is required")
            sys.exit(1)
    
    location = config.GCP_LOCATION
    model_name = config.GEMINI_MODEL
    
    # Initialize Vertex AI
    print(f"\nInitializing Vertex AI...")
    print(f"  Project: {project_id}")
    print(f"  Location: {location}")
    
    try:
        vertexai.init(project=project_id, location=location)
        print("Vertex AI initialized (using ADC)")
    except Exception as e:
        print(f"\nFailed to initialize Vertex AI: {e}")
        print("\nMake sure you've run: gcloud auth application-default login")
        sys.exit(1)
    
    # Initialize Gemini model
    print(f"\nLoading Gemini model: {model_name}...")
    
    system_instruction = """You are a helpful Python coding assistant with code execution capabilities.

When the user asks you to perform tasks that require computation or code:
1. Write clear, well-commented Python code
2. Put the code in ```python code blocks
3. I will automatically execute it and show you the results
4. Explain what the code does before or after the code block

The execution environment has common packages like numpy, pandas, matplotlib pre-installed.
Keep code concise and focused on the task."""

    try:
        model = GenerativeModel(
            model_name,
            system_instruction=system_instruction
        )
        print(f"Gemini model ready: {model_name}")
    except Exception as e:
        print(f"Failed to load model: {e}")
        sys.exit(1)
    
    # Choose executor type
    print("\n" + "="*70)
    print("EXECUTION ENVIRONMENT SELECTION")
    print("="*70)
    
    executor_type = input("\nUse VM or E2B for code execution? (vm/e2b): ").strip().lower()
    
    if executor_type == "vm":
        print("\nVM Configuration")
        print("-" * 70)
        
        # Get VM details from config or prompt
        vm_ip = config.VM_IP
        if not vm_ip:
            vm_ip = input("Enter VM IP address: ").strip()
            if not vm_ip:
                print("Error: VM IP is required")
                sys.exit(1)
        
        username = config.VM_USERNAME
        if not username:
            username = input("Enter VM username: ").strip()
            if not username:
                print("Error: VM username is required")
                sys.exit(1)
        
        vm_name = config.VM_NAME or None
        vm_zone = config.VM_ZONE or "us-central1-a"
        
        print(f"\n  VM IP: {vm_ip}")
        print(f"  Username: {username}")
        if vm_name:
            print(f"  VM Name: {vm_name}")
            print(f"  Zone: {vm_zone}")
        
        executor = VMExecutor(
            vm_ip=vm_ip,
            username=username,
            vm_name=vm_name,
            zone=vm_zone
        )
    else:
        print("\nUsing E2B Sandbox")
        executor = CodeExecutor()
    
    # Initialize executor
    await executor.start()
    
    # Generation config
    generation_config = GenerationConfig(
        temperature=0.7,
        top_p=0.95,
        top_k=40,
        max_output_tokens=2048,
    )
    
    print("="*70)
    print("\nExamples:")
    print("  - Calculate the first 10 Fibonacci numbers")
    print("  - Create a bar chart of [1, 4, 9, 16, 25]")
    print("  - Generate 100 random numbers and find their mean\n")
    print("Type 'quit' or 'exit' to end the session\n")
    print("="*70 + "\n")
    
    # Main conversation loop
    conversation_history = []
    
    try:
        while True:
            # Get user input
            user_input = input("You: ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("\nGoodbye!")
                break
            
            if not user_input:
                continue
            
            # Add to conversation history
            conversation_history.append({
                "role": "user",
                "parts": [user_input]
            })
            
            # Call Gemini
            print("\nGemini is thinking...\n")
            
            try:
                # Start a chat with history
                chat = model.start_chat(history=conversation_history[:-1])
                response = chat.send_message(
                    user_input,
                    generation_config=generation_config
                )
                
                agent_text = response.text
                
                # Add response to history
                conversation_history.append({
                    "role": "model",
                    "parts": [agent_text]
                })
                
                print(f"Agent: {agent_text}\n")
                
                # Extract and execute code blocks
                code_blocks = extract_code_blocks(agent_text)
                
                if code_blocks:
                    print("─"*70)
                    print(f"Found {len(code_blocks)} code block(s) to execute")
                    print("─"*70)
                    
                    for i, code in enumerate(code_blocks, 1):
                        print(f"\nExecuting code block {i}/{len(code_blocks)}...\n")
                        
                        # Execute the code
                        result = await executor.execute(code)
                        
                        if result['success']:
                            if result['output']:
                                print(f"Output:")
                                print(result['output'])
                            
                            if result['stderr']:
                                print(f"\nWarnings:")
                                print(result['stderr'])
                            
                            if result['error']:
                                print(f"\nError:")
                                print(result['error'])
                                
                                # Optionally feed error back to Gemini
                                error_feedback = f"\nThe code execution resulted in an error:\n{result['error']}\n\nCan you fix this?"
                                print(f"\nSending error back to Gemini for debugging...")
                        else:
                            print(f"Execution failed: {result['error']}")
                    
                    print("\n" + "─"*70 + "\n")
                else:
                    # No code blocks found
                    pass
            
            except Exception as e:
                print(f"\nError calling Gemini: {e}\n")
                # Remove the failed exchange from history
                conversation_history = conversation_history[:-1]
    
    except KeyboardInterrupt:
        print("\n\nInterrupted by user. Goodbye!")
    
    finally:
        # Cleanup
        await executor.stop()


if __name__ == "__main__":
    asyncio.run(main())