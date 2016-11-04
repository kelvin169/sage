r"""
Knots

AUTHORS:

- Miguel Angel Marco Buzunariz
- Amit Jamadagni
"""

#*****************************************************************************
#       Copyright (C) 2014   Travis Scrimshaw <tscrim at ucdavis.edu>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# (at your option) any later version.
#                  http://www.gnu.org/licenses/
#*****************************************************************************

from sage.knots.link import Link
from sage.rings.integer import Integer
from sage.rings.finite_rings.integer_mod import Mod


class Knot(Link):
    """
    A knot.

    A knot is defined as embedding of the circle `\mathbb{S}^1` in the
    3-dimensional sphere `\mathbb{S}^3`, considered up to ambient isotopy.
    They represent the physical idea of a knotted rope, but with the
    particularity that the rope is closed. That is, the ends of the rope
    are joined.

    .. SEEALSO::

        :class:`Link`

    INPUT:

    - ``data`` -- see :class:`Link` for the allowable inputs
    - ``check`` -- optional, default ``True``. If ``True``, make sure
      that the data define a knot, not a link

    EXAMPLES:

    We construct the knot `8_{14}` and compute some invariants::

        sage: B = BraidGroup(4)
        sage: K = Knot(B([1,1,1,2,-1,2,-3,2,-3]))

    .. PLOT::
        :width: 300 px

        B = BraidGroup(4)
        K = Knot(B([1,1,1,2,-1,2,-3,2,-3]))
        sphinx_plot(K.plot())

    ::

        sage: K.alexander_polynomial()
        -2*t^-2 + 8*t^-1 - 11 + 8*t - 2*t^2
        sage: K.jones_polynomial()
        t^7 - 3*t^6 + 4*t^5 - 5*t^4 + 6*t^3 - 5*t^2 + 4*t + 1/t - 2
        sage: K.determinant()
        31
        sage: K.signature()
        -2

    REFERENCES:

    - :wikipedia:`Knot_(mathematics)`

    .. TODO::

        - Make a class Knots for the monoid of all knots and have this be an
          element in that monoid.
    """
    def __init__(self, data, check=True):
        """
        Initialize ``self``.

        TESTS::

            sage: B = BraidGroup(8)
            sage: K = Knot(B([-1, -1, -1, 2, 1, -2, 3, -2, 3]))
            sage: TestSuite(K).run()
            sage: K = Knot(B([1, -2, 1, -2]))
            sage: TestSuite(K).run()
            sage: K = Knot([[1, 1, 2, 2]])
            sage: TestSuite(K).run()

        The following is not a knot: it has two components. ::

            sage: Knot([[[1, 2], [-2, -1]], [1, -1]])
            Traceback (most recent call last):
            ...
            ValueError: the input has more than 1 connected component

            sage: Knot([[[1, 2], [-2, -1]], [1, -1]], check=False)
            Knot represented by 2 crossings
        """
        Link.__init__(self, data)
        if check:
            if self.number_of_components() != 1:
                raise ValueError("the input has more than 1 connected component")

    def __repr__(self):
        """
        Return a string representation.

        EXAMPLES::

            sage: B = BraidGroup(8)
            sage: K = Knot(B([1, 2, 1, 2]))
            sage: K
            Knot represented by 4 crossings
            sage: K = Knot([[1, 7, 2, 6], [7, 3, 8, 2], [3, 11, 4, 10], [11, 5, 12, 4], [14, 5, 1, 6], [13, 9, 14, 8], [12, 9, 13, 10]])
            sage: K
            Knot represented by 7 crossings
        """
        pd_len = len(self.pd_code())
        return 'Knot represented by {} crossings'.format(pd_len)

    def dt_code(self):
        """
        Return the DT code of ``self``.

        ALGORITHM:

        The DT code is generated by the following way:

        Start moving along the knot, as we encounter the crossings we
        start numbering them, so every crossing has two numbers assigned to
        it once we have traced the entire knot. Now we take the even number
        associated with every crossing.

        The following sign convention is to be followed:

        Take the even number with a negative sign if it is an overcrossing
        that we are encountering.

        OUTPUT: DT code representation of the knot

        EXAMPLES::

            sage: K = Knot([[1,5,2,4],[5,3,6,2],[3,1,4,6]])
            sage: K.dt_code()
            [4, 6, 2]
            sage: B = BraidGroup(4)
            sage: K = Knot(B([1, 2, 1, 2]))
            sage: K.dt_code()
            [4, -6, 8, -2]
            sage: K = Knot([[[1, -2, 3, -4, 5, -1, 2, -3, 4, -5]], [1, 1, 1, 1, 1]])
            sage: K.dt_code()
            [6, 8, 10, 2, 4]
        """
        b = self.braid().Tietze()
        N = len(b)
        label = [0 for i in range(2 * N)]
        string = 1
        next_label = 1
        type1 = 0
        crossing = 0
        while next_label <= 2 * N:
            string_found = False
            for i in range(crossing, N):
                if abs(b[i]) == string or abs(b[i]) == string - 1:
                    string_found = True
                    crossing = i
                    break
            if not string_found:
                for i in range(0, crossing):
                    if abs(b[i]) == string or abs(b[i]) == string - 1:
                        string_found = True
                        crossing = i
                        break
            assert label[2 * crossing + next_label % 2] != 1, "invalid knot"

            label[2 * crossing + next_label % 2] = next_label
            next_label = next_label + 1
            if type1 == 0:
                if b[crossing] < 0:
                    type1 = 1
                else:
                    type1 = -1
            else:
                type1 = -1 * type1
                if ((abs(b[crossing]) == string and b[crossing] * type1 > 0)
                    or (abs(b[crossing]) != string and b[crossing] * type1 < 0)):
                    if next_label % 2 == 1:
                        label[2 * crossing] = label[2 * crossing] * -1
            if abs(b[crossing]) == string:
                string = string + 1
            else:
                string = string - 1
            crossing = crossing + 1
        code = [0 for i in range(N)]
        for i in range(N):
            for j in range(N):
                if label[2 * j + 1] == 2 * i + 1:
                    code[i] = label[2 * j]
                    break
        return code

    def arf_invariant(self):
        """
        Return the Arf invariant.

        EXAMPLES::

            sage: B = BraidGroup(4)
            sage: K = Knot(B([-1, 2, 1, 2]))
            sage: K.arf_invariant()
            0
            sage: B = BraidGroup(8)
            sage: K = Knot(B([-2, 3, 1, 2, 1, 4]))
            sage: K.arf_invariant()
            0
            sage: K = Knot(B([1, 2, 1, 2]))
            sage: K.arf_invariant()
            1
        """
        a = self.alexander_polynomial()
        if Mod(a(-1), 8) == 1 or Mod(a(-1), 8) == 7:
            return 0

        return 1

    def connected_sum(self, other):
        r"""
        Return the oriented connected sum of ``self`` and ``other``.

        .. NOTE::

            We give the knots an orientation based upon the braid
            representation.

        INPUT:

        - ``other`` -- a knot

        OUTPUT:

        A knot equivalent to the connected sum of ``self`` and ``other``.

        EXAMPLES::

            sage: B = BraidGroup(2)
            sage: trefoil = Knot(B([1,1,1]))
            sage: K = trefoil.connected_sum(trefoil); K
            Knot represented by 7 crossings
            sage: K.braid()
            s0^3*s2^3*s1

        .. PLOT::
            :width: 300 px

            B = BraidGroup(2)
            trefoil = Knot(B([1,1,1]))
            K = trefoil.connected_sum(trefoil)
            sphinx_plot(K.plot())

        ::

            sage: rev_trefoil = Knot(B([-1,-1,-1]))
            sage: K = trefoil.connected_sum(rev_trefoil); K
            Knot represented by 7 crossings
            sage: K.braid()
            s0^3*s2^-3*s1

        .. PLOT::
            :width: 300 px

            B = BraidGroup(2)
            t = Knot(B([1,1,1]))
            tr = Knot(B([-1,-1,-1]))
            K = t.connected_sum(tr)
            sphinx_plot(K.plot())

        REFERENCES:

        - :wikipedia:`Connected_sum`
        """
        from sage.groups.braid import BraidGroup
        b1 = self.braid()
        b2 = other.braid()

        b1s = b1.strands()
        b2s = b2.strands()

        B = BraidGroup(b1s + b2s)

        return Knot(B(list(b1.Tietze())
                      + [(abs(i) + b2s) * Integer(i).sign() for i in b2.Tietze()]
                      + [b1s]))

    def fundamental_group(self):
        r"""
        Compute the Wirtinger presentation of the fundamental group of
        the complement of ``self``.
        
        OUTPUT:
        
        - A finitely presented group. Its presentation is the Wirtinger
          presentation of the knot.
          
        EXAMPLES::
        
            sage: K = Knot([[[1,-2,3,-1,2,-3]],[1,1,1]])
            sage: K.fundamental_group()
            Finitely presented group < x0, x1, x2 |
                x2*x1*x2^-1*x0^-1, x1*x0*x1^-1*x2^-1, x0*x2*x0^-1*x1^-1 >
        """
        from sage.groups.free_group import FreeGroup
        gauss_code = self.oriented_gauss_code()
        crossing_list = gauss_code[0][0]
        negative_indices = [i for i,val in enumerate(crossing_list) if val < 0]
        gens = [crossing_list[negative_indices[i]:negative_indices[i+1]+1]
                for i in range(len(negative_indices)-1)]
        gens.append(crossing_list[negative_indices[-1]:]
                    + crossing_list[:negative_indices[0]+1])
        relations = []
        for cros in range(len(gauss_code[1])):
            gi = [g for g in gens if cros+1 in g][0]
            gj = [g for g in gens if -(cros+1) == g[-1]][0]
            giind = gens.index(gi)
            gjind = gens.index(gj)
            gkind = gjind + 1
            if gkind >= len(gens):
                gkind = 0
            if gauss_code[1][cros] > 0:
                relations.append([giind+1, gkind+1, -giind-1, -gjind-1])
            else:
                relations.append([giind+1, gjind+1, -giind-1, -gkind-1])
        F = FreeGroup(len(gens))
        return F.quotient(relations)

