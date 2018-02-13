from sklearn import tree
import graphviz 
from networkx.drawing.nx_agraph import graphviz_layout
import networkx as nx
import matplotlib


X = [[0, 0], [1, 1]]
Y = [0, 1]
clf = tree.DecisionTreeClassifier()
clf = clf.fit(X, Y)
# above training is done

#next classfy

print clf.predict([[2., 2.]])
print clf.predict([[0.50, 0.50]])
print clf.predict([[0.10, 0.60]])
print clf.predict_proba([[0.50, 0.50]])
print clf.predict_proba([[0.51, 0.51]])

dot_data = tree.export_graphviz(clf, out_file=None)
graph = graphviz.Source(dot_data)
graph.render("iris")  #render to 'iris.pdf'

def draw(graph):
    pos = graphviz_layout(graph)
    #nx.draw(graph, pos)
    nx.draw_networkx(graph, 
         node_size = [16 * graph.degree(n) for n in graph],
         node_color = [graph.depth[n] for n in graph],
         with_labels = False)
#
#    nx.drawing.draw_graphviz(graph,
#         node_size = [16 * graph.degree(n) for n in graph],
#         node_color = [graph.depth[n] for n in graph],
#         with_labels = False)
    matplotlib.pyplot.show()

#draw(graph)

