def assert_list_equiv(this, that):
    """
    Lists are having difficulty with equivalence, so let's try this.
    """
    assert len(this) == len(that)
    for i in range(len(this)):
        assert this[i] == that[i]