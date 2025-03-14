import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
import random
import os

# Import the DisjointSet and MazeGenerator classes from the original file
from maze_generator import DisjointSet, MazeGenerator
from maze_solver import MazeSolver

class MazeGeneratorApp(tk.Tk):
    def __init__(self):
        super().__init__()
        
        self.title("Maze Generator")
        self.geometry("800x700")
        self.resizable(True, True)
        
        self.maze_generator = None
        self.maze = None
        self.maze_solver = None
        self.zoom_level = 1.0  # Default zoom level
        
        # Initialize view position (center of the maze)
        self.view_x = 0
        self.view_y = 0
        
        # Variables for tracking mouse drag
        self.drag_start_x = 0
        self.drag_start_y = 0
        self.is_dragging = False
        
        self.create_widgets()
        
    def create_widgets(self):
        # Create a frame for input controls
        input_frame = ttk.LabelFrame(self, text="Maze Settings")
        input_frame.pack(fill="x", padx=10, pady=10)
        
        # Width input
        ttk.Label(input_frame, text="Width:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.width_var = tk.StringVar(value="20")
        width_entry = ttk.Entry(input_frame, textvariable=self.width_var, width=10)
        width_entry.grid(row=0, column=1, padx=5, pady=5, sticky="w")
        
        # Height input
        ttk.Label(input_frame, text="Height:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.height_var = tk.StringVar(value="20")
        height_entry = ttk.Entry(input_frame, textvariable=self.height_var, width=10)
        height_entry.grid(row=1, column=1, padx=5, pady=5, sticky="w")
        
        # Difficulty selection
        difficulty_frame = ttk.LabelFrame(input_frame, text="Difficulty")
        difficulty_frame.grid(row=0, column=2, rowspan=2, padx=10, pady=5, sticky="nsew")
        
        self.difficulty_var = tk.StringVar(value="normal")
        for i, diff in enumerate(["easy", "normal", "hard"]):
            ttk.Radiobutton(difficulty_frame, text=diff.capitalize(), 
                           variable=self.difficulty_var, value=diff).pack(pady=2)
        
        # Button frame
        button_frame = ttk.Frame(input_frame)
        button_frame.grid(row=0, column=3, rowspan=2, padx=10, pady=5)
        
        # Generate button
        generate_button = ttk.Button(button_frame, text="Generate Maze", command=self.generate_maze)
        generate_button.pack(pady=2)
        
        # Save button
        save_button = ttk.Button(button_frame, text="Save Maze", command=self.save_maze)
        save_button.pack(pady=2)
        
        # Solve button
        solve_button = ttk.Button(button_frame, text="Solve Maze", command=self.solve_maze)
        solve_button.pack(pady=2)
        
        # Create a zoom control frame
        zoom_frame = ttk.LabelFrame(self, text="Zoom Controls")
        zoom_frame.pack(fill="x", padx=10, pady=5)
        
        # Zoom in button
        zoom_in_button = ttk.Button(zoom_frame, text="+", width=3, command=self.zoom_in)
        zoom_in_button.pack(side=tk.LEFT, padx=5, pady=5)
        
        # Zoom out button
        zoom_out_button = ttk.Button(zoom_frame, text="-", width=3, command=self.zoom_out)
        zoom_out_button.pack(side=tk.LEFT, padx=5, pady=5)
        
        # Reset zoom button
        reset_zoom_button = ttk.Button(zoom_frame, text="Reset Zoom", command=self.reset_zoom)
        reset_zoom_button.pack(side=tk.LEFT, padx=5, pady=5)
        
        # Zoom level display
        self.zoom_label = ttk.Label(zoom_frame, text="Zoom: 100%")
        self.zoom_label.pack(side=tk.LEFT, padx=20, pady=5)
        
        # Create a frame for the maze display
        self.display_frame = ttk.LabelFrame(self, text="Maze Display")
        self.display_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Create a Figure and Canvas for matplotlib
        self.figure = plt.Figure(figsize=(6, 6), dpi=100)
        self.canvas = FigureCanvasTkAgg(self.figure, self.display_frame)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)
        
        # Bind mouse events for dragging
        self.canvas.get_tk_widget().bind("<ButtonPress-1>", self.on_mouse_press)
        self.canvas.get_tk_widget().bind("<B1-Motion>", self.on_mouse_drag)
        self.canvas.get_tk_widget().bind("<ButtonRelease-1>", self.on_mouse_release)
        
        # Bind mouse wheel for zooming
        self.canvas.get_tk_widget().bind("<MouseWheel>", self.on_mouse_wheel)  # Windows
        self.canvas.get_tk_widget().bind("<Button-4>", self.on_mouse_wheel)  # Linux scroll up
        self.canvas.get_tk_widget().bind("<Button-5>", self.on_mouse_wheel)  # Linux scroll down
        
        # Status bar
        self.status_var = tk.StringVar(value="Ready. Enter dimensions and click 'Generate Maze'.")
        status_bar = ttk.Label(self, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Made by HYU attribution
        made_by_label = ttk.Label(self, text="Made by HYU", font=("Arial", 8))
        made_by_label.pack(side=tk.BOTTOM, anchor=tk.E, padx=10, pady=2)
    
    def generate_maze(self):
        try:
            # Get dimensions from input fields
            width = int(self.width_var.get())
            height = int(self.height_var.get())
            
            # Validate input
            if width <= 0 or height <= 0:
                messagebox.showerror("Invalid Input", "Width and height must be positive integers.")
                return
            
            # Update status
            self.status_var.set(f"Generating {width}x{height} maze...")
            self.update_idletasks()  # Force GUI update
            
            # Reset state
            self.maze_solver = None
            if hasattr(self, 'figure'):
                self.figure.clear()
            
            # Generate the maze with selected difficulty
            self.maze_generator = MazeGenerator(width, height, self.difficulty_var.get())
            self.maze_generator.set_animation_callback(self.update_maze_display)
            self.maze = self.maze_generator.generate()
            
            # Reset view and zoom
            self.view_x = 0
            self.view_y = 0
            self.zoom_level = 1.0
            
            # Display the maze
            self.display_maze()
            
            # Update status
            self.status_var.set(f"Maze generated successfully ({width}x{height}).")
            
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter valid integers for width and height.")
            self.status_var.set("Error: Invalid input. Please enter positive integers.")
        finally:
            # Re-enable controls whether generation succeeds or fails
            self.enable_controls()
    
    def update_maze_display(self, maze):
        """Update the maze display during generation/solving."""
        self.maze = maze
        self.display_maze()
        self.update_idletasks()
    
    def display_maze(self):
        if self.maze is None:
            return
        
        # Clear the figure
        self.figure.clear()
        
        # Create a new subplot
        ax = self.figure.add_subplot(111)
        
        # If solver exists and has a solution, use its visualization
        if self.maze_solver and self.maze_solver.solution_path:
            solution_maze = self.maze_solver.get_solution_maze()
            ax.imshow(solution_maze)
        else:
            ax.imshow(self.maze, cmap='binary')
            
        ax.set_title(f"Maze ({self.maze_generator.width}x{self.maze_generator.height})")
        ax.axis('off')
        
        # Apply zoom level
        ax.set_xlim(self.get_zoom_limits(0, self.maze.shape[1]))
        ax.set_ylim(self.get_zoom_limits(0, self.maze.shape[0]))
        
        # Redraw the canvas
        self.canvas.draw()
    
    def get_zoom_limits(self, min_val, max_val):
        """Calculate the limits for zooming with panning."""
        total_range = max_val - min_val
        half_range = total_range / (2 * self.zoom_level)
        
        # Calculate center based on view position
        if min_val == 0 and max_val == self.maze.shape[1]:  # X-axis
            center = total_range / 2 + self.view_x * (total_range / 10)
        else:  # Y-axis
            center = total_range / 2 + self.view_y * (total_range / 10)
        
        # Ensure we don't pan outside the maze
        min_limit = max(min_val, center - half_range)
        max_limit = min(max_val, center + half_range)
        
        return [min_limit, max_limit]
    
    def zoom_in(self):
        """Increase zoom level."""
        self.zoom_level = min(5.0, self.zoom_level * 1.2)  # Limit max zoom to 5x
        self.update_zoom_display()
        if self.maze is not None:
            self.display_maze()
    
    def zoom_out(self):
        """Decrease zoom level."""
        self.zoom_level = max(0.2, self.zoom_level / 1.2)  # Limit min zoom to 0.2x
        self.update_zoom_display()
        if self.maze is not None:
            self.display_maze()
    
    def reset_zoom(self):
        """Reset zoom to default level."""
        self.zoom_level = 1.0
        self.view_x = 0
        self.view_y = 0
        self.update_zoom_display()
        if self.maze is not None:
            self.display_maze()
            
    def pan(self, dx, dy):
        """Pan the view in the specified direction."""
        # Scale the pan amount based on zoom level
        pan_scale = 0.5 / self.zoom_level
        
        # Update view position
        self.view_x += dx * pan_scale
        self.view_y += dy * pan_scale
        
    def solve_maze(self):
        if self.maze is None:
            messagebox.showerror("No Maze", "Please generate a maze first.")
            return
        
        # Create solver if not exists
        if self.maze_solver is None:
            self.maze_solver = MazeSolver(self.maze)
        
        # Create dialog for algorithm selection
        dialog = tk.Toplevel(self)
        dialog.title("Select Solving Algorithm")
        dialog.geometry("350x250")  # Increased width and height
        dialog.transient(self)
        dialog.grab_set()
        
        # Algorithm selection
        ttk.Label(dialog, text="Select Algorithm:").pack(pady=10)
        algorithm_var = tk.StringVar(value="astar")
        algorithms = [("A* Search", "astar"), 
                     ("Breadth-First Search", "bfs"),
                     ("Depth-First Search", "dfs"),
                     ("Dijkstra's Algorithm", "dijkstra")]
        
        for text, value in algorithms:
            ttk.Radiobutton(dialog, text=text, value=value, 
                           variable=algorithm_var).pack(pady=5)
        
        # Store selected algorithm and solve maze
        def select_and_solve():
            self.selected_algorithm = algorithm_var.get()
            dialog.destroy()
            
            # Solve the maze with selected algorithm
            self.status_var.set("Solving maze...")
            self.update_idletasks()
            
            solution = self.maze_solver.solve(algorithm=self.selected_algorithm,
                                            callback=self.update_maze_display)
            
            if solution:
                self.display_maze()
                self.status_var.set("Maze solved successfully!")
            else:
                self.status_var.set("No solution found.")
                messagebox.showinfo("No Solution", "No solution exists for this maze.")
        
        # Add solve button to dialog with increased padding and width
        solve_button = ttk.Button(dialog, text="Solve with Selected Algorithm", command=select_and_solve)
        solve_button.pack(pady=15, padx=20, fill=tk.X)  # Increased padding
        
        # Center the dialog on the main window
        dialog.update_idletasks()
        x = self.winfo_x() + (self.winfo_width() - dialog.winfo_width()) // 2
        y = self.winfo_y() + (self.winfo_height() - dialog.winfo_height()) // 2
        dialog.geometry(f"+{x}+{y}")
        
        # Wait for dialog to close
        self.wait_window(dialog)

        
        # Limit panning to reasonable bounds
        self.view_x = max(-5, min(5, self.view_x))
        self.view_y = max(-5, min(5, self.view_y))
        
        # Update the display
        if self.maze is not None:
            self.display_maze()
            self.status_var.set(f"View position: ({self.view_x:.1f}, {self.view_y:.1f}), Zoom: {int(self.zoom_level * 100)}%")
    
    def on_mouse_press(self, event):
        """Handle mouse press event to start dragging."""
        if self.maze is not None and self.zoom_level > 1.0:
            self.is_dragging = True
            self.drag_start_x = event.x
            self.drag_start_y = event.y
    
    def on_mouse_drag(self, event):
        """Handle mouse drag event to pan the view."""
        if self.is_dragging and self.maze is not None:
            # Calculate the drag distance
            dx = self.drag_start_x - event.x
            dy = self.drag_start_y - event.y
            
            # Scale the movement based on zoom level and canvas size
            scale_x = 0.01 * self.zoom_level
            scale_y = 0.01 * self.zoom_level
            
            # Update view position
            self.view_x += dx * scale_x
            self.view_y += dy * scale_y
            
            # Limit panning to reasonable bounds
            self.view_x = max(-5, min(5, self.view_x))
            self.view_y = max(-5, min(5, self.view_y))
            
            # Update drag start position
            self.drag_start_x = event.x
            self.drag_start_y = event.y
            
            # Update status bar without redrawing the maze
            self.status_var.set(f"View position: ({self.view_x:.1f}, {self.view_y:.1f}), Zoom: {int(self.zoom_level * 100)}%")
    
    def on_mouse_release(self, event):
        """Handle mouse release event to stop dragging."""
        if self.is_dragging and self.maze is not None:
            # Only redraw the maze when mouse is released
            self.display_maze()
        self.is_dragging = False
    
    def update_zoom_display(self):
        """Update the zoom level display."""
        zoom_percentage = int(self.zoom_level * 100)
        self.zoom_label.config(text=f"Zoom: {zoom_percentage}%")
        self.status_var.set(f"Zoom level: {zoom_percentage}%")
    
    def on_mouse_wheel(self, event):
        """Handle mouse wheel event to zoom in/out."""
        if self.maze is None:
            return
        
        # Store the current zoom level before changing it
        old_zoom = self.zoom_level
        
        # Get the mouse position in canvas coordinates
        x, y = event.x, event.y
        
        # Convert canvas coordinates to figure coordinates
        # First get the axes from the figure
        if not hasattr(self, 'figure') or len(self.figure.axes) == 0:
            # If no axes available, use default zooming
            if event.num == 5 or event.delta < 0:  # Scroll down or Windows delta negative
                self.zoom_out()
            elif event.num == 4 or event.delta > 0:  # Scroll up or Windows delta positive
                self.zoom_in()
            return
        
        ax = self.figure.axes[0]
        
        # Convert canvas coordinates to axes coordinates
        # transform expects a single argument that is a tuple of (x, y)
        x_fig, y_fig = ax.transAxes.inverted().transform((x, y))
        
        # Get the current view limits
        x_min, x_max = ax.get_xlim()
        y_min, y_max = ax.get_ylim()
        
        # Calculate the point in data coordinates
        x_data = x_min + (x_max - x_min) * x_fig
        y_data = y_min + (y_max - y_min) * y_fig
        
        # Determine the direction of the scroll and update zoom level
        if event.num == 5 or event.delta < 0:  # Scroll down or Windows delta negative
            self.zoom_level = max(0.2, self.zoom_level / 1.2)  # Limit min zoom to 0.2x
        elif event.num == 4 or event.delta > 0:  # Scroll up or Windows delta positive
            self.zoom_level = min(5.0, self.zoom_level * 1.2)  # Limit max zoom to 5x
        
        # Calculate the zoom ratio
        zoom_ratio = old_zoom / self.zoom_level
        
        # Adjust view position to keep the cursor point fixed
        # The adjustment depends on how far the cursor is from the center
        width, height = self.maze.shape[1], self.maze.shape[0]
        
        # Calculate normalized cursor position (-1 to 1 from center)
        cursor_x_norm = (x_data / width - 0.5) * 2
        cursor_y_norm = (y_data / height - 0.5) * 2
        
        # Adjust view position based on cursor position and zoom change
        self.view_x += cursor_x_norm * (1 - zoom_ratio) * 5
        self.view_y += cursor_y_norm * (1 - zoom_ratio) * 5
        
        # Limit panning to reasonable bounds
        self.view_x = max(-5, min(5, self.view_x))
        self.view_y = max(-5, min(5, self.view_y))
        
        # Update the zoom display
        self.update_zoom_display()
        
        # Redraw the maze with the new zoom level
        if self.maze is not None:
            self.display_maze()
            self.status_var.set(f"View position: ({self.view_x:.1f}, {self.view_y:.1f}), Zoom: {int(self.zoom_level * 100)}%")
        
        # Return 'break' to prevent the event from propagating
        return 'break'
    
    def save_maze(self):
        if self.maze is None:
            messagebox.showinfo("No Maze", "Please generate a maze first.")
            return
        
        # Ask for file location
        file_path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG files", "*.png"), ("All files", "*.*")],
            title="Save Maze As"
        )
        
        if not file_path:
            return  # User cancelled
        
        try:
            # Create a figure for saving
            plt.figure(figsize=(10, 10))
            
            # If maze is solved, save the solution visualization
            if self.maze_solver and self.maze_solver.solution_path:
                plt.imshow(self.maze_solver.get_solution_maze())
            else:
                plt.imshow(self.maze, cmap='binary')
            
            plt.axis('off')
            plt.title(f"Maze ({self.maze_generator.width}x{self.maze_generator.height})")
            plt.savefig(file_path)
            plt.close()
            
            self.status_var.set(f"Maze saved as {os.path.basename(file_path)}")
            messagebox.showinfo("Success", f"Maze saved as {file_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save maze: {str(e)}")
            self.status_var.set("Error: Failed to save maze.")


    def enable_controls(self):
        """Enable all control widgets after maze operations."""
        for widget in self.winfo_children():
            if isinstance(widget, (ttk.Frame, ttk.LabelFrame)):
                for child in widget.winfo_children():
                    if isinstance(child, (ttk.Button, ttk.Entry)):
                        child.configure(state='normal')
            elif isinstance(widget, (ttk.Button, ttk.Entry)):
                widget.configure(state='normal')

def main():
    app = MazeGeneratorApp()
    app.mainloop()

if __name__ == "__main__":
    main()