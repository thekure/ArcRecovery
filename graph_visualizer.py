from PyQt5.QtWidgets import QGraphicsView, QGraphicsScene
from PyQt5.QtGui import QPen
from PyQt5.QtCore import Qt
import networkx as nx

class GraphView(QGraphicsView):
    def __init__(self, graph, parent=None):
        super().__init__(parent)
        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)
        self.graph = graph
        self.draw_graph()

    def draw_graph(self):
        pos = nx.spring_layout(self.graph)
        for node, (x, y) in pos.items():
            self.scene.addEllipse(x * 500, y * 500, 20, 20)
            self.scene.addText(node).setPos(x * 500 + 10, y * 500 + 10)
        for src, dst in self.graph.edges():
            src_x, src_y = pos[src]
            dst_x, dst_y = pos[dst]
            line = self.scene.addLine(
                src_x * 500 + 10, 
                src_y * 500 + 10, 
                dst_x * 500 + 10, 
                dst_y * 500 + 10, 
                QPen(Qt.black)
            ) 