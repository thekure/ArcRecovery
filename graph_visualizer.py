from PyQt5.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsItem, QGraphicsEllipseItem, QGraphicsRectItem
from PyQt5.QtGui import QPen, QBrush, QColor, QFont, QPainter
from PyQt5.QtCore import Qt, pyqtSignal, QRectF
import networkx as nx

class PackageNodeItem(QGraphicsRectItem):
    """Custom QGraphicsItem for package nodes that can be clicked on."""
    def __init__(self, x, y, width, height, package_name, members, is_expandable=False, *args, **kwargs):
        super().__init__(x, y, width, height, *args, **kwargs)
        self.package_name = package_name
        self.members = members
        self.is_expandable = is_expandable
        self.setAcceptHoverEvents(True)
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)
        
    def mousePressEvent(self, event):
        # Pass the click event up to the parent view
        if self.scene() and self.scene().views():
            view = self.scene().views()[0]
            if hasattr(view, 'node_clicked'):
                view.node_clicked(self.package_name, self.members)
        super().mousePressEvent(event)
        
    def hoverEnterEvent(self, event):
        # Change cursor to pointing hand when hovering over a package node
        if self.scene() and self.scene().views():
            self.scene().views()[0].setCursor(Qt.PointingHandCursor)
        super().hoverEnterEvent(event)
        
    def hoverLeaveEvent(self, event):
        # Reset cursor when leaving the node
        if self.scene() and self.scene().views():
            self.scene().views()[0].setCursor(Qt.ArrowCursor)
        super().hoverLeaveEvent(event)

class GraphView(QGraphicsView):
    # Signal to notify parent when a package node is clicked
    package_clicked = pyqtSignal(str, list)
    
    def __init__(self, graph, parent=None, use_edge_weights=False):
        try:
            super().__init__(parent)
            print(f"Initializing GraphView with {len(graph.nodes())} nodes and {len(graph.edges())} edges")
            
            if not isinstance(graph, nx.Graph):
                raise ValueError("Input must be a NetworkX graph")
                
            if len(graph.nodes()) == 0:
                raise ValueError("Cannot visualize an empty graph")
                
            print("Creating scene...")
            self.scene = QGraphicsScene(self)
            self.setScene(self.scene)
            self.graph = graph
            self.use_edge_weights = use_edge_weights
            self.setRenderHint(QPainter.Antialiasing)
            self.setRenderHint(QPainter.TextAntialiasing)
            
            # Enable dragging and proper view handling
            self.setDragMode(QGraphicsView.ScrollHandDrag)
            self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
            self.setResizeAnchor(QGraphicsView.AnchorUnderMouse)
            self.setViewportUpdateMode(QGraphicsView.FullViewportUpdate)
            
            print("Scene created, calling draw_graph...")
            self.draw_graph()
            
            # Fit the view to show all items
            self.fitInView(self.scene.itemsBoundingRect(), Qt.KeepAspectRatio)
            
        except Exception as e:
            print(f"Error in GraphView.__init__: {str(e)}")
            raise

    def node_clicked(self, package_name, members):
        """Handle click on package node by notifying parent widget."""
        print(f"Package node clicked: {package_name} with {len(members)} members")
        
        # Check if this is a package node that should be expandable
        is_package = False
        has_children = False
        
        for node, data in self.graph.nodes(data=True):
            if str(node) == package_name:
                is_package = data.get('is_package', False) or 'members' in data
                has_children = data.get('has_children', False)
                break
                
        if not is_package and not has_children:
            print(f"Node {package_name} is not a package node or has no children")
            return
            
        # Make sure we have members to pass along
        if not members or len(members) <= 1:
            members = [package_name]
            # Try to find all nodes that start with this package name
            for node in self.graph.nodes():
                node_str = str(node)
                if node_str.startswith(f"{package_name}."):
                    members.append(node_str)
            print(f"Expanded members list to {len(members)} items")
            
        # Emit the signal with package name and members
        self.package_clicked.emit(package_name, members)

    def wheelEvent(self, event):
        # Zoom in/out with mouse wheel
        factor = 1.2
        if event.angleDelta().y() < 0:
            factor = 1.0 / factor
        
        # Get the position before scaling
        old_pos = self.mapToScene(event.pos())
        
        # Scale the view
        self.scale(factor, factor)
        
        # Get the position after scaling
        new_pos = self.mapToScene(event.pos())
        
        # Move the scene to keep the mouse position fixed
        delta = new_pos - old_pos
        self.translate(delta.x(), delta.y())

    def draw_graph(self):
        try:
            print("Starting layout calculation...")
            # Use spring layout with more iterations and better parameters
            if len(self.graph) <= 10:
                # For small graphs, use larger k value to push nodes apart more
                pos = nx.spring_layout(self.graph, k=2.0, iterations=200, seed=42)
            else:
                # For larger graphs, tune parameters based on node count
                k_factor = max(0.8, min(2.0, 20 / len(self.graph)))
                pos = nx.spring_layout(self.graph, k=k_factor, iterations=150, seed=42)
                
                # Post-process positions to ensure minimal distance between nodes
                self.adjust_node_positions(pos)
                
            print(f"Layout calculated successfully for {len(self.graph.nodes())} nodes")
            
            # Get min and max size values for scaling if any node has a size attribute
            min_size, max_size = 20, 20  # Default size
            has_size_attr = any('size' in data for _, data in self.graph.nodes(data=True))
            is_grouped = any('members' in data for _, data in self.graph.nodes(data=True))
            
            if has_size_attr:
                # Find min and max sizes
                sizes = [data.get('size', 1) for _, data in self.graph.nodes(data=True)]
                if sizes:
                    min_val = min(sizes) if min(sizes) > 0 else 1
                    max_val = max(sizes)
                    
                    # Set min and max node sizes
                    min_size = 20
                    max_size = 40
                    
                    # For grouped nodes, allow even larger sizes
                    if is_grouped:
                        max_size = 50
                        
            # Scale the canvas based on node count
            scale_factor = 500
            if len(self.graph) < 5:
                scale_factor = 800  # More space for very small graphs
            elif len(self.graph) > 50:
                scale_factor = 400  # More compact for large graphs

            # First, draw all edges to ensure they're in the background
            print("Drawing edges...")
            for i, (src, dst) in enumerate(self.graph.edges()):
                if i % 100 == 0:
                    print(f"Drawing edge {i}/{len(self.graph.edges())}")
                try:
                    if src in pos and dst in pos:
                        src_x, src_y = pos[src]
                        dst_x, dst_y = pos[dst]
                        
                        # Determine line width based on edge weight
                        if self.use_edge_weights:
                            edge_data = self.graph.get_edge_data(src, dst)
                            edge_weight = edge_data.get('weight', 1) if edge_data else 1
                            # Use a more reasonable scaling for line width
                            line_width = min(0.5 + edge_weight * 0.5, 4)
                        else:
                            line_width = 0.5
                            
                        # Draw the edge
                        line = self.scene.addLine(
                            src_x * scale_factor, 
                            src_y * scale_factor, 
                            dst_x * scale_factor, 
                            dst_y * scale_factor, 
                            QPen(QColor(150, 150, 150, 180), line_width)  # Semi-transparent gray
                        )
                        # Ensure edges are drawn below nodes
                        line.setZValue(-1)
                except Exception as e:
                    print(f"Error drawing edge {src}->{dst}: {str(e)}")
            
            print("Starting node drawing...")
            # Now draw all nodes on top of the edges
            for i, node in enumerate(self.graph.nodes()):
                if i % 100 == 0:
                    print(f"Drawing node {i}/{len(pos)}")
                try:
                    # Get node attributes
                    node_data = self.graph.nodes[node]
                    is_package_node = node_data.get('is_package', False) or 'members' in node_data
                    has_children = node_data.get('has_children', False)
                    
                    # Determine node size based on attributes
                    if has_size_attr and 'size' in node_data:
                        # Scale the size between min_size and max_size
                        size_value = node_data['size']
                        if min_val == max_val:  # Avoid division by zero
                            node_size = min_size
                        else:
                            # Scale logarithmically to handle large differences
                            import math
                            scale_factor_size = (math.log(size_value + 1) - math.log(min_val + 1)) / (math.log(max_val + 1) - math.log(min_val + 1))
                            node_size = min_size + scale_factor_size * (max_size - min_size)
                    else:
                        node_size = min_size
                    
                    # Determine node color
                    # Default color for internal modules
                    node_color = QColor(200, 200, 255)  # Light blue
                    
                    # Use different colors for grouped package nodes
                    if is_package_node:
                        # Use orange for package groups - this applies to all levels
                        node_color = QColor(255, 200, 120)  # Orange
                        
                        # Ensure package nodes are at least medium size
                        node_size = max(node_size, 35)  
                    # Make very important nodes more prominent
                    elif has_size_attr and 'size' in node_data and node_data['size'] > (max_val * 0.8):
                        node_color = QColor(255, 150, 150)  # Light red for high importance
                    
                    # Get position
                    x, y = pos[node]
                    
                    # Draw node as ellipse or rectangle for packages
                    if is_package_node:
                        # Draw as rectangle for package nodes with clickable behavior
                        rect_size = node_size * 1.3
                        rect_x = x * scale_factor - rect_size/2
                        rect_y = y * scale_factor - rect_size/2
                        
                        # Check if this package is expandable
                        is_expandable = node_data.get('is_expandable', True) or node_data.get('has_children', False)
                        
                        # Create a custom package node item that can be clicked
                        package_item = PackageNodeItem(
                            rect_x, rect_y, rect_size, rect_size,
                            str(node), node_data.get('members', [node]),
                            is_expandable=is_expandable
                        )
                        package_item.setPen(QPen(Qt.black, 2))
                        package_item.setBrush(QBrush(node_color))
                        
                        # Add visual hint that this node is clickable
                        if is_expandable and node_data.get('has_children', False):
                            click_hint = self.scene.addText("👆")
                            click_hint.setPos(rect_x + rect_size - 15, rect_y - 5)
                        
                        self.scene.addItem(package_item)
                    else:
                        # Draw as ellipse for regular modules
                        ellipse = self.scene.addEllipse(
                            x * scale_factor - node_size/2, 
                            y * scale_factor - node_size/2, 
                            node_size, 
                            node_size,
                            QPen(Qt.black, 1),
                            QBrush(node_color)
                        )
                    
                    # Add label
                    # For longer names, show just the last part of the module path
                    display_name = str(node)
                    if len(display_name) > 25 and not is_package_node:  # If name is too long
                        parts = display_name.split('.')
                        if len(parts) > 2:
                            display_name = '...' + '.'.join(parts[-2:])  # Show only last two parts
                    
                    # For package nodes, show module count using the total_members attribute if available
                    if is_package_node:
                        # Use total_members if available, otherwise fall back to members
                        if 'total_members' in node_data:
                            member_count = node_data['total_members']
                        elif 'members' in node_data:
                            member_count = len(node_data['members'])
                        else:
                            member_count = 0
                            
                        # Strip any parts of the package name if at a deeper level
                        if '.' in display_name:
                            display_parts = display_name.split('.')
                            display_name = display_parts[-1]  # Just show the last part
                            
                        display_name = f"{display_name} ({member_count})"
                    
                    label = self.scene.addText(display_name)
                    font_size = 8
                    if is_package_node:
                        font_size = 10  # Larger font for package nodes
                        # Make the text bold
                        font = QFont("Arial", font_size)
                        font.setBold(True)
                        label.setFont(font)
                    else:
                        label.setFont(QFont("Arial", font_size))
                    
                    # Position label better
                    label_width = label.boundingRect().width()
                    label.setPos(x * scale_factor - label_width/2, y * scale_factor + node_size/2 + 5)
                except Exception as e:
                    print(f"Error drawing node {node}: {str(e)}")
                    raise
            
            print("Graph drawn successfully")
            # Set scene rect to include all items
            self.scene.setSceneRect(self.scene.itemsBoundingRect().adjusted(-50, -50, 50, 50))
            
        except Exception as e:
            print(f"Error in draw_graph: {str(e)}")
            raise ValueError(f"Error drawing graph: {str(e)}")
            
    def adjust_node_positions(self, pos):
        """Post-process node positions to prevent overlapping."""
        min_distance = 0.1  # Minimum distance between nodes
        
        # Repeat the adjustment a few times
        for _ in range(3):
            moved = False
            # Check all pairs of nodes
            nodes = list(pos.keys())
            for i in range(len(nodes)):
                for j in range(i+1, len(nodes)):
                    n1, n2 = nodes[i], nodes[j]
                    
                    # Calculate distance
                    x1, y1 = pos[n1]
                    x2, y2 = pos[n2]
                    dx = x2 - x1
                    dy = y2 - y1
                    distance = (dx**2 + dy**2)**0.5
                    
                    # If nodes are too close, push them apart
                    if distance < min_distance:
                        # Direction vector
                        if distance == 0:  # Exactly overlapping
                            import random
                            dx, dy = random.uniform(-0.1, 0.1), random.uniform(-0.1, 0.1)
                            distance = (dx**2 + dy**2)**0.5
                        
                        # Normalized direction vector
                        dx, dy = dx/distance, dy/distance
                        
                        # Move both nodes apart
                        push = (min_distance - distance) / 2
                        pos[n1] = (x1 - dx * push, y1 - dy * push)
                        pos[n2] = (x2 + dx * push, y2 + dy * push)
                        moved = True
            
            if not moved:
                break
        
        return pos 