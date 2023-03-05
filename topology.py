def get_topology(top_code):
    assert top_code in ['htmnj','htnjm','rrlh']
    if(top_code == 'htmnj'):
        top_G = {'A':['E'],'B':['E'],'C':['E'],'D':['E'],'E':['F']}
        edges = []
        for key,val in top_G.items():
            for node in val:
                edges.append(key+node)

        lengths = {'AE':200,'BE':200,'CE':200,'DE':200,'EF':200}

        input_edges = ['AE', 'BE', 'CE', 'DE']

        next_edge = {'AE':['EF'], 'BE':['EF'], 'CE':['EF'], 'DE':['EF'], 'EF':[None]}

        merges = [[['AE', 'BE', 'CE', 'DE'], 'EF']]
        
        
    elif(top_code == 'htnjm'):
        top_G = {'A':['D'],'B':['D'],'C':['D'],'D':['F'],'E':['F'], 'F':['H'], 'G':['H'], 'H':['J'], 'I':['J'], 'J':['K']}
        edges = []
        for key,val in top_G.items():
            for node in val:
                edges.append(key+node)

        lengths = {i:200 for i in edges}

        input_edges = ['AD', 'BD', 'CD', 'EF', 'GH', 'IJ']
        
        for edge in input_edges:
            lengths[edge] = 100

        next_edge = {'AD':['DF'], 'BD':['DF'], 'CD':['DF'], 'DF':['FH'], 'EF':['FH'], 'FH':['HJ'], 'GH':['HJ'], 'HJ':['JK'], 'IJ':['JK'], 'JK':[None]}

        merges = [[['AD', 'BD', 'CD'], 'DF'],[['DF','EF'],'FH'],[['FH','GH'],'HJ'],[['HJ','IJ'],'JK']]
        
        
    else:
        top_G = {'A':['E'],'B':['E'],'C':['E'],'D':['E'],'E':['F'], 'F':['G','H','I','J']}
        edges = []
        for key,val in top_G.items():
            for node in val:
                edges.append(key+node)

        lengths = {i:200 for i in edges}

        input_edges = ['AE', 'BE', 'CE', 'DE']
        lengths['EF'] = 80

        next_edge = {'AE':['EF'], 'BE':['EF'], 'CE':['EF'], 'DE':['EF'], 'EF':['FG','FH','FI','FJ'], 'FG':[None], 'FH':[None],\
                     'FI':[None], 'FJ':[None]}

        merges = [[['AE', 'BE', 'CE', 'DE'], 'EF']]
        
    return(edges,lengths,input_edges,next_edge,merges)