
from heuristics.AC import AC

#
# TODO: ALEX
#

class AC_simple(AC):
    '''
        Optimize the examination scheduling problem using shuffling of exam lists.
        
        data:        dictionary containing all relevant data
        gamma:       weighting factor for objectives
        
        returns x_ik y_il, objVal
    '''

    def __init__(self, data, gamma = 1.0):
        super(AC, self).__init__(data, gamma)
    

    def generate_colorings(self, num_ants):
        
        # TODO: Generate colourings
        # ...
        colorings = [ np.random.shuffle(np.arange(self.data[n])) for n in num_ants ]
        
        return colorings
    

if __name__ == '__main__':
    
    n = 10
    r = 10
    p = 10
    tseed = 295

    from model.instance import build_smart_random
    data = build_smart_random(n=n, r=r, p=p, tseed=tseed)    test_compare()

    num_ants = 10
    ac = AC_simple(data)
    colorings = ac.generate_colorings(num_ants)
    print colorings
    
    