from multiprocessing import Pool

def f(x):
    return len(x)

if __name__ == '__main__':
    p = Pool(2)
    
    xs = [ {1:2,2:3}, {4:2,5:4} ]
    
    print(p.map(f, xs))
 
