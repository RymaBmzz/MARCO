from pyminisolvers import minicard

class MinicardMapSolver:
    def __init__(self, n, bias=True):   # bias=True is a high/inclusion/MUS bias; False is a low/exclusion/MSS bias.
        self.n = n
        self.bias = bias
        if bias:
            self.k = n  # initial lower bound on # of True variables
        else:
            self.k = 0
        self.solver = minicard.Solver()
        while self.solver.nvars() < self.n:
            self.solver.new_var(self.bias)

        # add "bound-setting" variables
        while self.solver.nvars() < self.n*2:
            self.solver.new_var()

        # add cardinality constraint (comment is for high bias, maximal model;
        #                             becomes AtMostK for low bias, minimal model)
        # want: generic AtLeastK over all n variables
        # how: make AtLeast([n vars, n bound-setting vars], n)
        #      then, assume the desired k out of the n bound-setting vars.
        # e.g.: for real vars a,b,c: AtLeast([a,b,c, x,y,z], 3)
        #       for AtLeast 3: assume(-x,-y,-z)
        #       for AtLeast 1: assume(-x)
        # and to make AtLeast into an AtMost:
        #   AtLeast([lits], k) ==> AtMost([-lits], #lits-k)
        if self.bias:
            self.solver.add_atmost([-(x+1) for x in range(self.n * 2)], self.n)
        else:
            self.solver.add_atmost([(x+1) for x in range(self.n * 2)], self.n)

    def solve_with_bound(self, k):
        # same assumptions work both for high bias / atleast and for low bias / atmost
        return self.solver.solve([-(self.n+x+1) for x in range(k)] + [(self.n+k+x+1) for x in range(self.n-k)])

    def has_seed(self):
        '''
            Find the next-most-maximal model.
        '''
        if self.solve_with_bound(self.k):
            return True

        if self.bias:
            if not self.solve_with_bound(0):
                # no more models
                return False
        else:
            if not self.solve_with_bound(self.n):
                # no more models
                return False

        while not self.solve_with_bound(self.k):
            if self.bias:
                self.k -= 1
            else:
                self.k += 1

        assert 0 <= self.k <= self.n

        return True

    def get_seed(self):
        model = self.solver.get_model()
        seed = [i for i in range(self.n) if model[i]]
        # slower:
        #seed = set()
        #for i in range(self.n):
        #    if self.solver.model_value(i+1):
        #        seed.add(i)
        return seed

    def check_seed(self, seed):
        raise NotImplementedError  # TODO: how to check seeds when our instance has cardinality constraints in it...?
        
        return self.solver.solve(seed)

    def complement(self, aset):
        return set(range(self.n)) - aset

    def block_down(self, frompoint):
        comp = self.complement(frompoint)
        if comp:
            self.solver.add_clause([i+1 for i in comp])
        else:
            # *could* be empty (if instance is SAT)
            self.solver.add_clause( [] )

    def block_up(self, frompoint):
        if frompoint:
            self.solver.add_clause([-(i+1) for i in frompoint])
        else:
            # *could* be empty (if instance is SAT)
            self.solver.add_clause( [] )

    def block_above_size(self, size):
        self.solver.add_atmost([(x+1) for x in range(self.n)], size)
        self.k = min(size, self.k)

    def block_below_size(self, size):
        self.solver.add_atmost([-(x+1) for x in range(self.n)], self.n-size)
        self.k = min(size, self.k)
