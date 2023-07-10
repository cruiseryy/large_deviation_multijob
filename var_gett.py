from utils import var_retriever

var_ = ['RAINNC', 'SMOIS', 'SMCREL']

test = var_retriever()

for v in var_:
    test.get_var(var_ = v)
