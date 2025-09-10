"""
Phase 7: Advanced Workflow Automation - Visual Workflow Designer
Provides drag-and-drop workflow builder with real-time execution monitoring
"""

import json
import uuid
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
import asyncio
from pathlib import Path

try:
    import tkinter as tk
    from tkinter import ttk, messagebox, filedialog
    import tkinter.font as tkFont
    GUI_AVAILABLE = True
except ImportError:
    GUI_AVAILABLE = False

from .workflow_engine import WorkflowEngine, WorkflowStateStore
from .workflow_triggers import TriggerManager
from .workflow_actions import ActionLibrary

@dataclass
class WorkflowNode:
    """Represents a visual workflow node"""
    id: str
    type: str  # 'trigger', 'action', 'condition', 'parallel'
    name: str
    parameters: Dict[str, Any]
    position: Tuple[int, int]
    connections: List[str]  # Connected node IDs
    metadata: Dict[str, Any]

@dataclass
class WorkflowCanvas:
    """Visual workflow representation"""
    id: str
    name: str
    description: str
    nodes: List[WorkflowNode]
    variables: Dict[str, Any]
    created_at: datetime
    modified_at: datetime

class WorkflowDesigner:
    """Visual workflow designer with drag-and-drop interface"""
    
    def __init__(self, data_dir: str = "workflow_data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        
        # Core components
        self.engine = WorkflowEngine(data_dir)
        self.action_library = ActionLibrary()
        self.trigger_manager = TriggerManager()
        
        # Designer state
        self.current_workflow: Optional[WorkflowCanvas] = None
        self.selected_node: Optional[str] = None
        self.clipboard_node: Optional[WorkflowNode] = None
        self.zoom_level = 1.0
        self.canvas_offset = (0, 0)
        
        # GUI components
        self.root: Optional[tk.Tk] = None
        self.canvas: Optional[tk.Canvas] = None
        self.property_panel: Optional[ttk.Frame] = None
        self.node_palette: Optional[ttk.Frame] = None
        
        # Available node types
        self.node_templates = {
            'triggers': {
                'git_trigger': {'name': 'Git Changes', 'icon': '🔄', 'color': '#4CAF50'},
                'file_trigger': {'name': 'File Changes', 'icon': '📁', 'color': '#2196F3'},
                'schedule_trigger': {'name': 'Schedule', 'icon': '⏰', 'color': '#FF9800'},
                'webhook_trigger': {'name': 'Webhook', 'icon': '🌐', 'color': '#9C27B0'}
            },
            'actions': {
                'generate_code': {'name': 'Generate Code', 'icon': '⚡', 'color': '#F44336'},
                'run_tests': {'name': 'Run Tests', 'icon': '🧪', 'color': '#4CAF50'},
                'deploy': {'name': 'Deploy', 'icon': '🚀', 'color': '#2196F3'},
                'notify': {'name': 'Notify', 'icon': '📢', 'color': '#FF9800'},
                'analyze_code': {'name': 'Analyze Code', 'icon': '🔍', 'color': '#9C27B0'},
                'backup_data': {'name': 'Backup', 'icon': '💾', 'color': '#607D8B'}
            },
            'control': {
                'condition': {'name': 'Condition', 'icon': '❓', 'color': '#795548'},
                'parallel': {'name': 'Parallel', 'icon': '⚡', 'color': '#FF5722'},
                'wait': {'name': 'Wait', 'icon': '⏸️', 'color': '#9E9E9E'},
                'loop': {'name': 'Loop', 'icon': '🔄', 'color': '#3F51B5'}
            }
        }
    
    def create_gui(self) -> bool:
        """Create the visual designer interface"""
        if not GUI_AVAILABLE:
            print("GUI not available - tkinter not installed")
            return False
        
        self.root = tk.Tk()
        self.root.title("Aeonforge Workflow Designer - Phase 7")
        self.root.geometry("1400x900")
        self.root.configure(bg='#2b2b2b')
        
        # Create menu bar
        self._create_menu_bar()
        
        # Create main layout
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create toolbar
        self._create_toolbar(main_frame)
        
        # Create paned window for main content
        paned_window = ttk.PanedWindow(main_frame, orient=tk.HORIZONTAL)
        paned_window.pack(fill=tk.BOTH, expand=True, pady=(5, 0))
        
        # Create node palette (left panel)
        self._create_node_palette(paned_window)
        
        # Create canvas area (center)
        self._create_canvas(paned_window)
        
        # Create property panel (right)
        self._create_property_panel(paned_window)
        
        # Bind events
        self._bind_events()
        
        return True
    
    def _create_menu_bar(self):
        """Create application menu bar"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="New Workflow", command=self.new_workflow, accelerator="Ctrl+N")
        file_menu.add_command(label="Open Workflow", command=self.open_workflow, accelerator="Ctrl+O")
        file_menu.add_command(label="Save Workflow", command=self.save_workflow, accelerator="Ctrl+S")
        file_menu.add_command(label="Save As...", command=self.save_workflow_as)
        file_menu.add_separator()
        file_menu.add_command(label="Import", command=self.import_workflow)
        file_menu.add_command(label="Export", command=self.export_workflow)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        
        # Edit menu
        edit_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Edit", menu=edit_menu)
        edit_menu.add_command(label="Undo", command=self.undo_action, accelerator="Ctrl+Z")
        edit_menu.add_command(label="Redo", command=self.redo_action, accelerator="Ctrl+Y")
        edit_menu.add_separator()
        edit_menu.add_command(label="Copy Node", command=self.copy_node, accelerator="Ctrl+C")
        edit_menu.add_command(label="Paste Node", command=self.paste_node, accelerator="Ctrl+V")
        edit_menu.add_command(label="Delete Node", command=self.delete_node, accelerator="Delete")
        edit_menu.add_separator()
        edit_menu.add_command(label="Select All", command=self.select_all, accelerator="Ctrl+A")
        
        # Workflow menu
        workflow_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Workflow", menu=workflow_menu)
        workflow_menu.add_command(label="Validate", command=self.validate_workflow, accelerator="F5")
        workflow_menu.add_command(label="Test Run", command=self.test_workflow, accelerator="F6")
        workflow_menu.add_command(label="Deploy", command=self.deploy_workflow, accelerator="F7")
        workflow_menu.add_separator()
        workflow_menu.add_command(label="View Executions", command=self.view_executions)
        workflow_menu.add_command(label="Monitor Performance", command=self.monitor_performance)
        
        # View menu
        view_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="View", menu=view_menu)
        view_menu.add_command(label="Zoom In", command=self.zoom_in, accelerator="Ctrl++")
        view_menu.add_command(label="Zoom Out", command=self.zoom_out, accelerator="Ctrl+-")
        view_menu.add_command(label="Reset Zoom", command=self.reset_zoom, accelerator="Ctrl+0")
        view_menu.add_separator()
        view_menu.add_command(label="Center Canvas", command=self.center_canvas)
        view_menu.add_command(label="Fit to Window", command=self.fit_to_window)
    
    def _create_toolbar(self, parent):
        """Create toolbar with common actions"""
        toolbar = ttk.Frame(parent)
        toolbar.pack(fill=tk.X, pady=(0, 5))
        
        # Workflow controls
        ttk.Button(toolbar, text="▶️ Run", command=self.run_workflow).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(toolbar, text="⏸️ Pause", command=self.pause_workflow).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(toolbar, text="⏹️ Stop", command=self.stop_workflow).pack(side=tk.LEFT, padx=(0, 5))
        
        ttk.Separator(toolbar, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=10)
        
        # Design tools
        ttk.Button(toolbar, text="🔍 Validate", command=self.validate_workflow).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(toolbar, text="📊 Monitor", command=self.monitor_performance).pack(side=tk.LEFT, padx=(0, 5))
        
        # Status label
        self.status_label = ttk.Label(toolbar, text="Ready")
        self.status_label.pack(side=tk.RIGHT)
    
    def _create_node_palette(self, parent):
        """Create node palette for drag-and-drop"""
        palette_frame = ttk.Frame(parent, width=200)
        parent.add(palette_frame)
        
        # Palette title
        title_label = ttk.Label(palette_frame, text="Node Palette", font=('Arial', 12, 'bold'))
        title_label.pack(pady=10)
        
        # Create scrollable frame
        canvas = tk.Canvas(palette_frame, width=180)
        scrollbar = ttk.Scrollbar(palette_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Add node categories
        for category, nodes in self.node_templates.items():
            # Category header
            cat_frame = ttk.LabelFrame(scrollable_frame, text=category.title(), padding=5)
            cat_frame.pack(fill=tk.X, padx=5, pady=2)
            
            # Nodes in category
            for node_type, config in nodes.items():
                node_button = tk.Button(
                    cat_frame,
                    text=f"{config['icon']} {config['name']}",
                    bg=config['color'],
                    fg='white',
                    relief=tk.RAISED,
                    borderwidth=2,
                    command=lambda nt=node_type, cfg=config: self.add_node_to_canvas(nt, cfg)
                )
                node_button.pack(fill=tk.X, pady=1)
                
                # Make draggable
                node_button.bind("<Button-1>", lambda e, nt=node_type: self.start_drag_node(e, nt))
    
    def _create_canvas(self, parent):
        """Create main workflow canvas"""
        canvas_frame = ttk.Frame(parent)
        parent.add(canvas_frame)
        
        # Canvas with scrollbars
        self.canvas = tk.Canvas(
            canvas_frame,
            bg='#f0f0f0',
            scrollregion=(0, 0, 2000, 2000)
        )
        
        h_scrollbar = ttk.Scrollbar(canvas_frame, orient="horizontal", command=self.canvas.xview)
        v_scrollbar = ttk.Scrollbar(canvas_frame, orient="vertical", command=self.canvas.yview)
        
        self.canvas.configure(xscrollcommand=h_scrollbar.set, yscrollcommand=v_scrollbar.set)
        
        # Grid layout
        self.canvas.grid(row=0, column=0, sticky="nsew")
        h_scrollbar.grid(row=1, column=0, sticky="ew")
        v_scrollbar.grid(row=0, column=1, sticky="ns")
        
        canvas_frame.grid_rowconfigure(0, weight=1)
        canvas_frame.grid_columnconfigure(0, weight=1)
        
        # Draw grid
        self._draw_grid()
    
    def _create_property_panel(self, parent):
        """Create property editing panel"""
        self.property_panel = ttk.Frame(parent, width=300)
        parent.add(self.property_panel)
        
        # Title
        title_label = ttk.Label(self.property_panel, text="Properties", font=('Arial', 12, 'bold'))
        title_label.pack(pady=10)
        
        # Property notebook for different tabs
        self.prop_notebook = ttk.Notebook(self.property_panel)
        self.prop_notebook.pack(fill=tk.BOTH, expand=True, padx=5)
        
        # General properties tab
        self.general_tab = ttk.Frame(self.prop_notebook)
        self.prop_notebook.add(self.general_tab, text="General")
        
        # Parameters tab
        self.params_tab = ttk.Frame(self.prop_notebook)
        self.prop_notebook.add(self.params_tab, text="Parameters")
        
        # Connections tab
        self.connections_tab = ttk.Frame(self.prop_notebook)
        self.prop_notebook.add(self.connections_tab, text="Connections")
        
        # Initial empty state
        self._show_no_selection()
    
    def _bind_events(self):
        """Bind keyboard and mouse events"""
        # Canvas events
        self.canvas.bind("<Button-1>", self.on_canvas_click)
        self.canvas.bind("<B1-Motion>", self.on_canvas_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_canvas_release)
        self.canvas.bind("<Button-3>", self.on_canvas_right_click)
        self.canvas.bind("<Double-Button-1>", self.on_canvas_double_click)
        
        # Keyboard shortcuts
        self.root.bind("<Control-n>", lambda e: self.new_workflow())
        self.root.bind("<Control-o>", lambda e: self.open_workflow())
        self.root.bind("<Control-s>", lambda e: self.save_workflow())
        self.root.bind("<Control-c>", lambda e: self.copy_node())
        self.root.bind("<Control-v>", lambda e: self.paste_node())
        self.root.bind("<Delete>", lambda e: self.delete_node())
        self.root.bind("<F5>", lambda e: self.validate_workflow())
        self.root.bind("<F6>", lambda e: self.test_workflow())
        self.root.bind("<F7>", lambda e: self.deploy_workflow())
        
        # Mouse wheel for zoom
        self.canvas.bind("<Control-MouseWheel>", self.on_mouse_wheel)
    
    def _draw_grid(self):
        """Draw background grid"""
        self.canvas.delete("grid")
        
        # Grid parameters
        grid_size = int(20 * self.zoom_level)
        width = int(self.canvas.winfo_width())
        height = int(self.canvas.winfo_height())
        
        # Draw vertical lines
        for i in range(0, width, grid_size):
            self.canvas.create_line(i, 0, i, height, fill="#e0e0e0", tags="grid")
        
        # Draw horizontal lines
        for i in range(0, height, grid_size):
            self.canvas.create_line(0, i, width, i, fill="#e0e0e0", tags="grid")
    
    def add_node_to_canvas(self, node_type: str, config: Dict[str, Any]):
        """Add a new node to the canvas"""
        if not self.current_workflow:
            self.new_workflow()
        
        # Create new node
        node_id = str(uuid.uuid4())
        position = (200 + len(self.current_workflow.nodes) * 50, 100)
        
        node = WorkflowNode(
            id=node_id,
            type=node_type,
            name=config['name'],
            parameters={},
            position=position,
            connections=[],
            metadata={'color': config['color'], 'icon': config['icon']}
        )
        
        self.current_workflow.nodes.append(node)
        self._draw_node(node)
        
        # Select the new node
        self.select_node(node_id)
        
        self._update_status(f"Added {config['name']} node")
    
    def _draw_node(self, node: WorkflowNode):
        """Draw a workflow node on canvas"""
        x, y = node.position
        color = node.metadata.get('color', '#607D8B')
        icon = node.metadata.get('icon', '⚙️')
        
        # Node rectangle
        node_rect = self.canvas.create_rectangle(
            x, y, x + 120, y + 60,
            fill=color,
            outline='#333',
            width=2,
            tags=(f"node_{node.id}", "node")
        )
        
        # Node icon and text
        self.canvas.create_text(
            x + 20, y + 20,
            text=icon,
            font=('Arial', 16),
            tags=(f"node_{node.id}", "node_icon")
        )
        
        self.canvas.create_text(
            x + 60, y + 40,
            text=node.name,
            font=('Arial', 10),
            fill='white',
            tags=(f"node_{node.id}", "node_text")
        )
        
        # Connection points
        self.canvas.create_oval(
            x + 115, y + 25, x + 125, y + 35,
            fill='white',
            outline='#333',
            tags=(f"node_{node.id}", "connection_out")
        )
        
        self.canvas.create_oval(
            x - 5, y + 25, x + 5, y + 35,
            fill='white',
            outline='#333',
            tags=(f"node_{node.id}", "connection_in")
        )
    
    def new_workflow(self):
        """Create a new workflow"""
        workflow_id = str(uuid.uuid4())
        self.current_workflow = WorkflowCanvas(
            id=workflow_id,
            name="New Workflow",
            description="",
            nodes=[],
            variables={},
            created_at=datetime.now(),
            modified_at=datetime.now()
        )
        
        self.canvas.delete("all")
        self._draw_grid()
        self._update_status("New workflow created")
    
    def save_workflow(self):
        """Save current workflow"""
        if not self.current_workflow:
            return
        
        workflow_file = self.data_dir / f"{self.current_workflow.id}.json"
        
        with open(workflow_file, 'w') as f:
            json.dump(asdict(self.current_workflow), f, indent=2, default=str)
        
        self._update_status(f"Workflow saved: {self.current_workflow.name}")
    
    def validate_workflow(self):
        """Validate current workflow"""
        if not self.current_workflow:
            messagebox.showwarning("No Workflow", "No workflow to validate")
            return
        
        issues = []
        
        # Check for trigger nodes
        trigger_nodes = [n for n in self.current_workflow.nodes if n.type.endswith('_trigger')]
        if not trigger_nodes:
            issues.append("Workflow must have at least one trigger")
        
        # Check for orphaned nodes
        connected_nodes = set()
        for node in self.current_workflow.nodes:
            connected_nodes.update(node.connections)
        
        for node in self.current_workflow.nodes:
            if node.id not in connected_nodes and not node.type.endswith('_trigger'):
                issues.append(f"Node '{node.name}' is not connected")
        
        # Check for cycles
        if self._has_cycles():
            issues.append("Workflow contains cycles")
        
        if issues:
            messagebox.showerror("Validation Issues", "\n".join(issues))
        else:
            messagebox.showinfo("Validation", "Workflow is valid!")
        
        return len(issues) == 0
    
    def run_workflow(self):
        """Run the current workflow"""
        if not self.current_workflow or not self.validate_workflow():
            return
        
        # Convert canvas to engine workflow
        engine_workflow = self._canvas_to_engine_workflow()
        
        # Execute asynchronously
        asyncio.create_task(self._execute_workflow_async(engine_workflow))
        
        self._update_status("Workflow execution started")
    
    async def _execute_workflow_async(self, workflow):
        """Execute workflow asynchronously"""
        try:
            execution = await self.engine.execute_workflow(workflow.id)
            self._update_status(f"Workflow completed: {execution.status}")
        except Exception as e:
            self._update_status(f"Workflow failed: {str(e)}")
            messagebox.showerror("Execution Error", str(e))
    
    def _canvas_to_engine_workflow(self):
        """Convert canvas workflow to engine workflow"""
        # This would convert the visual workflow to the engine format
        # Implementation depends on engine requirements
        pass
    
    def _has_cycles(self) -> bool:
        """Check if workflow has cycles"""
        # Simple cycle detection using DFS
        visited = set()
        rec_stack = set()
        
        def dfs(node_id: str) -> bool:
            if node_id in rec_stack:
                return True
            if node_id in visited:
                return False
            
            visited.add(node_id)
            rec_stack.add(node_id)
            
            node = next((n for n in self.current_workflow.nodes if n.id == node_id), None)
            if node:
                for conn_id in node.connections:
                    if dfs(conn_id):
                        return True
            
            rec_stack.remove(node_id)
            return False
        
        for node in self.current_workflow.nodes:
            if node.id not in visited:
                if dfs(node.id):
                    return True
        
        return False
    
    def select_node(self, node_id: str):
        """Select a workflow node"""
        # Clear previous selection
        self.canvas.delete("selection")
        
        # Highlight selected node
        node = next((n for n in self.current_workflow.nodes if n.id == node_id), None)
        if node:
            x, y = node.position
            self.canvas.create_rectangle(
                x - 3, y - 3, x + 123, y + 63,
                outline='#FFD700',
                width=3,
                tags="selection"
            )
            
            self.selected_node = node_id
            self._show_node_properties(node)
    
    def _show_node_properties(self, node: WorkflowNode):
        """Show properties for selected node"""
        # Clear existing property widgets
        for widget in self.general_tab.winfo_children():
            widget.destroy()
        
        # General properties
        ttk.Label(self.general_tab, text="Name:").pack(anchor='w', padx=5, pady=2)
        name_var = tk.StringVar(value=node.name)
        name_entry = ttk.Entry(self.general_tab, textvariable=name_var)
        name_entry.pack(fill='x', padx=5, pady=2)
        name_entry.bind('<KeyRelease>', lambda e: setattr(node, 'name', name_var.get()))
        
        ttk.Label(self.general_tab, text="Type:").pack(anchor='w', padx=5, pady=2)
        ttk.Label(self.general_tab, text=node.type).pack(anchor='w', padx=5, pady=2)
        
        ttk.Label(self.general_tab, text="ID:").pack(anchor='w', padx=5, pady=2)
        ttk.Label(self.general_tab, text=node.id[:8] + "...").pack(anchor='w', padx=5, pady=2)
    
    def _show_no_selection(self):
        """Show empty properties when nothing selected"""
        for widget in self.general_tab.winfo_children():
            widget.destroy()
        
        ttk.Label(
            self.general_tab,
            text="Select a node to view properties",
            font=('Arial', 10, 'italic')
        ).pack(expand=True)
    
    def _update_status(self, message: str):
        """Update status bar"""
        if hasattr(self, 'status_label'):
            self.status_label.config(text=message)
        print(f"Status: {message}")
    
    # Event handlers
    def on_canvas_click(self, event):
        """Handle canvas click"""
        # Check if clicked on a node
        item = self.canvas.find_closest(event.x, event.y)[0]
        tags = self.canvas.gettags(item)
        
        node_tag = next((tag for tag in tags if tag.startswith('node_')), None)
        if node_tag:
            node_id = node_tag.split('_', 1)[1]
            self.select_node(node_id)
        else:
            self.selected_node = None
            self._show_no_selection()
    
    def on_canvas_drag(self, event):
        """Handle canvas drag"""
        pass  # Implement node dragging
    
    def on_canvas_release(self, event):
        """Handle canvas release"""
        pass
    
    def on_canvas_right_click(self, event):
        """Handle right click context menu"""
        pass
    
    def on_canvas_double_click(self, event):
        """Handle double click to edit"""
        pass
    
    def on_mouse_wheel(self, event):
        """Handle mouse wheel zoom"""
        if event.delta > 0:
            self.zoom_in()
        else:
            self.zoom_out()
    
    def zoom_in(self):
        """Zoom in on canvas"""
        self.zoom_level = min(self.zoom_level * 1.2, 3.0)
        self._redraw_canvas()
    
    def zoom_out(self):
        """Zoom out on canvas"""
        self.zoom_level = max(self.zoom_level / 1.2, 0.3)
        self._redraw_canvas()
    
    def reset_zoom(self):
        """Reset zoom to 100%"""
        self.zoom_level = 1.0
        self._redraw_canvas()
    
    def _redraw_canvas(self):
        """Redraw canvas with current zoom"""
        self.canvas.delete("all")
        self._draw_grid()
        
        if self.current_workflow:
            for node in self.current_workflow.nodes:
                self._draw_node(node)
    
    # Placeholder methods for remaining functionality
    def open_workflow(self): pass
    def save_workflow_as(self): pass
    def import_workflow(self): pass
    def export_workflow(self): pass
    def undo_action(self): pass
    def redo_action(self): pass
    def copy_node(self): pass
    def paste_node(self): pass
    def delete_node(self): pass
    def select_all(self): pass
    def test_workflow(self): pass
    def deploy_workflow(self): pass
    def view_executions(self): pass
    def monitor_performance(self): pass
    def pause_workflow(self): pass
    def stop_workflow(self): pass
    def center_canvas(self): pass
    def fit_to_window(self): pass
    def start_drag_node(self, event, node_type): pass

def main():
    """Run the workflow designer"""
    designer = WorkflowDesigner()
    
    if designer.create_gui():
        designer.root.mainloop()
    else:
        print("Workflow Designer CLI mode")
        print("Available commands: new, save, load, validate, run, exit")
        
        while True:
            cmd = input("workflow> ").strip().lower()
            
            if cmd == "exit":
                break
            elif cmd == "new":
                designer.new_workflow()
                print("New workflow created")
            elif cmd == "validate":
                if designer.validate_workflow():
                    print("Workflow is valid")
            elif cmd.startswith("save"):
                designer.save_workflow()
            else:
                print("Unknown command. Available: new, save, validate, run, exit")

if __name__ == "__main__":
    main()