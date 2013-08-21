import publication
import networkx as nx
import re
from sets import Set
import matplotlib.pyplot as plt
#import sys




class arbol:

    def __init__(self):
        self.G=nx.DiGraph()
        self.list_author = Set([])
        self.list_collaborators = Set([])
        self.list_years = Set([])
        self.list_journals = Set ([])
        self.list_types = Set ([])
        self.list_objetcs = Set([])
        self.list_valid_authors = Set([])
        self.object_tmp = publication.publication()

    def leer(self):
        input_file=open("archivo.bib","r+")
        researchers_file = open ("researchers.txt","r+")
        for line in researchers_file:
                if '\n' in line and line.__len__>1:
                    self.list_author.add(line[:-1])
                
        researchers_file.close()
        
        #####

        
        for line in input_file:
            objeto = self.object_tmp
            if '@'  in line:
                try:
                    
                    type_pub = re.search('@(.+?){',line).group(1)
                    key_pub = re.search('{(.+?),',line).group(1)
                    self.list_types.add(type_pub)
                    
                    #if not (self.object_tmp.is_empty()):
    
                    self.list_objetcs.add(objeto)
                        
                    self.object_tmp = publication.publication()
                        
                    self.object_tmp.idp = key_pub
                        
                    self.object_tmp.type = type_pub                        
                        
                except AttributeError:
                    type_pub = ''
                    key_pub =  ''
            
            elif 'author' in line:
                try:
                    collaborators_pub = re.search('{(.+$)',line).group(1)
                    collaborators_pub = collaborators_pub[:-2]
                    collaborators_list = self.obtenerListaAutores(collaborators_pub)
                    for item in collaborators_list:
                        self.list_collaborators.add(item)
                        objeto.author.add(item)
                        
                        
                except AttributeError:
                    collaborators_pub = ''
            
            elif 'title' in line and not 'booktitle ' in line:
                try:
                    title_pub = re.search('{(.+?)}',line).group(1)
                    objeto.title = title_pub
                except AttributeError:
                    title_pub = ''
            elif 'journal' in line:
                try:
                    journal_pub = re.search('{(.+?)}',line).group(1)
                    self.list_journals.add(journal_pub)
                    objeto.journal = journal_pub
                except AttributeError:
                    journal_pub=''
            elif 'year' in line:
                try:
                    year_pub = re.search('{(.+?)}',line).group(1)
                    self.list_years.add(year_pub)
                    objeto.year = year_pub
                except AttributeError:
                    year_pub =''

        self.list_objetcs.add(objeto)
        input_file.close()
    
    
    def obtenerListaAutores(self,entrada):
    
            delimiters=" and ", ""
            regexPattern = '|'.join(map(re.escape, delimiters)) 
            #re.escape allows to build the pattern automatically and have the delimiters escaped nicely.
            return  re.split(regexPattern, entrada)
    

    def construir_arbol(self):
    
        self.G.add_node("publication",leaf='0')

        self.G.add_node("type",leaf='0')
        self.G.add_node("author",leaf='0')
        self.G.add_node("journal",leaf='0')
        self.G.add_node("year",leaf='0')
    
    
        self.G.add_edge("type","publication")
        self.G.add_edge("author","publication")
        self.G.add_edge("journal","publication")
        self.G.add_edge("year","publication")
    
        self.leer()
    
    
        self.list_years = sorted(self.list_years)
        self.list_author = sorted (self.list_author)
        self.list_journals = sorted (self.list_journals)
        self.list_collaborators = sorted(self.list_collaborators)
                
        for item in self.list_author:
            if item in self.list_collaborators:
                self.G.add_node(item,leaf='0')
                self.G.add_edge(item,"author")
                self.list_valid_authors.add(item)
                
        for item in self.list_types:    
            if item != '':
                self.G.add_node(item,leaf='0')
                self.G.add_edge(item,"type")
    
    
        for item in self.list_years:
            if item != '':
                self.G.add_node(item,leaf='0')
                self.G.add_edge(item,"year")
                
        for item in self.list_journals:
            if item != '':
                self.G.add_node(item,leaf='0')
                self.G.add_edge(item,"journal")
                
        for item in self.list_objetcs:
            for elem in item.author:         
                if self.G.has_node(elem):
                    self.G.add_node(item.idp, data = item, leaf='1')
                    self.G.add_edge(item.idp, elem)             
            if item.year in self.list_years:
                self.G.add_node(item.idp, data = item, leaf='1')
                self.G.add_edge(item.idp, item.year)
            if item.type in self.list_types:
                self.G.add_node(item.idp, data = item, leaf='1')
                self.G.add_edge(item.idp, item.type)
            if item.journal in self.list_journals:
                self.G.add_node(item.idp, data = item, leaf='1')
                self.G.add_edge(item.idp, item.journal)

                
        
    def is_related(self,list_objects,concept):
        flag=False
        list_result=Set([])
        if self.G.__contains__(concept):
            list_result=self.extension(concept, list_result)
            
            for item in list_objects:
                if item.idp in list_result:
                    flag=True
                    break
                
        return flag
    
    def deep_extension(self,focus,list_objects):
        
        if self.G.__contains__(focus):
            
            if self.G.predecessors(focus)==[]:
                
                list_objects.add(focus)
            else:
                for item in self.G.predecessors(focus):
                    self.deep_extension(item,list_objects)
    ## A diferencia de deep_extension, la lista resultante es regresada, no en los argumentos
    # eso se hizo para la recursividad en deep_extension    
    def extension(self,focus,list_resultante):
            self.deep_extension(focus, list_resultante)
            lista = (n for n,d in self.G.nodes_iter(data=True) if d['leaf']=='1' and n in list_resultante)
            list_a = Set([])
            for item in lista:
                list_a.add(item)
            return list_a
           

                        
    def set_conceptos(self, list_objects, root, list_concepts):

        list_obj_item = Set([])
        if self.G.__contains__(root):
            if not (self.G.predecessors(root)==[]):
                for item in self.G.predecessors(root):
                    lista = self.extension(item,list_obj_item)
                    list_obj_item=Set([]) #limpiar
                    for i in lista:
                        if i in list_objects:
                            list_concepts.add(root)
                        break
                    self.set_conceptos(list_objects, item, list_concepts)
                    
                                
    def valido(self, concepto, list_concepts):
        list_pub = Set([])
        list_a = self.extension(concepto, list_pub)
        list_result = Set([])
        self.set_conceptos(list_a, "publication", list_result)
        for item in list_result:
            if item in self.G.predecessors(concepto):
                list_concepts.add(item)
       
    
    def action(self):
        
        self.construir_arbol()
        
        print self.list_objetcs
        print self.is_related(self.list_objetcs, "author")
        print self.is_related(self.list_objetcs, "Rajsbaum, Sergio")
        print self.is_related(self.list_objetcs, "2011")
        print self.is_related(self.list_objetcs, "Urrutia, Jorge")
        print self.is_related(self.list_objetcs, "book")
        
        
                
        list_a=Set([])
        lista = self.extension("author", list_a)
        print  "extension author",lista

        list_a.clear() 
        self.valido("author",list_a)
        print "valido author",list_a
        
        list_a.clear() 
        self.extension("type",list_a)
        print "extension type",list_a
        
        list_a.clear() 
        self.valido("type",list_a)
        print "valido type",list_a  
        
        
        
 
            
        
        
 
        for item in self.G.nodes(data=True):
            print item
        #print self.G.edges(nbunch=None, data=True)

        count = 1   
        for item in self.list_objetcs:
            if item.title!="":
                print  count,") " ,item.title, '\n', item.author, '\n', item.year, '\n',item.journal, '\n',item.idp,item.type,'\n\n'
                count = count + 1

        list_a.clear()
        print "conceptos\n\n"
               
        for a in self.list_objetcs:
            list_a.add(a.idp)
            
        list_b = Set([])
        self.set_conceptos(list_a, "publication", list_b)
        print list_b
        
        pos = nx.shell_layout(self.G)
        nx.draw(self.G, pos)
        plt.show()        
