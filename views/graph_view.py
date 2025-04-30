from PyQt5.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsItem, QGraphicsRectItem
from PyQt5.QtGui import QPen, QBrush, QColor, QFont, QPainter
from PyQt5.QtCore import Qt, pyqtSignal, QRectF
import networkx as nx

class PackageNodeItem(QGraphicsRectItem):
    """Custom QGraphicsItem for package nodes that can be clicked on."""
    def __init__(self, x, y, width, height, package_name, members=None, is_expandable=False):
        super().__init__(x, y, width, height)
        self.package_name = package_name
        self.members = members or [package_name]
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
    
    def __init__(self, graph=None, parent=None):
        super().__init__(parent)
        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)
        self.graph = graph or nx.DiGraph()
        
        # Set up view options
        self.setRenderHint(QPainter.Antialiasing)
        self.setRenderHint(QPainter.TextAntialiasing)
        self.setDragMode(QGraphicsView.ScrollHandDrag)
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.AnchorUnderMouse)
        self.setViewportUpdateMode(QGraphicsView.FullViewportUpdate)
        
        if graph and graph.nodes():
            self.draw_graph()
    
    def set_graph(self, graph):
        """Update the view with a new graph."""
        self.scene.clear()
        self.graph = graph
        if graph and graph.nodes():
            self.draw_graph()
            self.fitInView(self.scene.itemsBoundingRect(), Qt.KeepAspectRatio)
    
    def node_clicked(self, package_name, members):
        """Handle click on package node by notifying parent widget."""
        self.package_clicked.emit(package_name, members)

    def wheelEvent(self, event):
        # Zoom in/out with mouse wheel
        factor = 1.2
        if event.angleDelta().y() < 0:
            factor = 1.0 / factor
        
        # Get the position before scaling
        old_pos = self.mapToScene(event.pos())
        self.scale(factor, factor)
        new_pos = self.mapToScene(event.pos())
        
        # Move the scene to keep the mouse position fixed
        delta = new_pos - old_pos
        self.translate(delta.x(), delta.y())

    def draw_graph(self):
        """Draw the graph visualization."""
        try:
            if not self.graph or len(self.graph) == 0:
                return
                
            # Calculate node positions
            pos = nx.spring_layout(self.graph, k=1.0, iterations=100, seed=42)
            
            # Scale for display
            scale_factor = 500
            
            # Draw edges first so they appear behind nodes
            for src, dst in self.graph.edges():
                if src in pos and dst in pos:
                    src_x, src_y = pos[src]
                    dst_x, dst_y = pos[dst]
                    
                    # Draw the edge
                    line = self.scene.addLine(
                        src_x * scale_factor, 
                        src_y * scale_factor, 
                        dst_x * scale_factor, 
                        dst_y * scale_factor, 
                        QPen(QColor(150, 150, 150, 180), 1)
                    )
                    line.setZValue(-1)
            
            # Draw nodes
            for node in self.graph.nodes():
                if node in pos:
                    x, y = pos[node]
                    
                    # Get node display properties
                    node_data = self.graph.nodes[node]
                    is_package = node_data.get('is_package', False)
                    is_expandable = node_data.get('is_expandable', False)
                    members = node_data.get('members', [str(node)])
                    
                    # Default size
                    node_size = 30
                    
                    # Create node representation
                    if is_package:
                        # Package nodes are rectangles
                        rect_width = node_size * 1.5
                        rect_height = node_size
                        
                        node_item = PackageNodeItem(
                            x * scale_factor - rect_width/2, 
                            y * scale_factor - rect_height/2,
                            rect_width, rect_height,
                            str(node), members, is_expandable
                        )
                        node_item.setBrush(QBrush(QColor(200, 230, 255)))
                        node_item.setPen(QPen(QColor(70, 130, 180), 2))
                    else:
                        # Regular modules are circles
                        node_item = self.scene.addEllipse(
                            x * scale_factor - node_size/2,
                            y * scale_factor - node_size/2,
                            node_size, node_size,
                            QPen(QColor(100, 100, 100), 1),
                            QBrush(QColor(220, 220, 220))
                        )
                    
                    # Add node label
                    label_text = str(node).split('.')[-1]  # Just show the last part of the name
                    text_item = self.scene.addText(label_text)
                    text_item.setFont(QFont("Arial", 8))
                    
                    # Center the text on the node
                    text_width = text_item.boundingRect().width()
                    text_height = text_item.boundingRect().height()
                    text_item.setPos(
                        x * scale_factor - text_width/2,
                        y * scale_factor + node_size/2 + 2
                    )
            
            # Fit view to the scene
            self.fitInView(self.scene.itemsBoundingRect(), Qt.KeepAspectRatio)
            
        except Exception as e:
            print(f"Error drawing graph: {str(e)}") 