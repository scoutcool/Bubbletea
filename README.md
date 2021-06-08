### Creating virtual environments
`python3 -m venv <DIR>`
`source <DIR>/bin/activate`

### Install Earlgrey
Earlgrey is published at pypi test for now.
`pip3 install --index-url https://test.pypi.org/simple/ --no-deps example-pkg-earlgrey`

### Earlgrey usage
#### The graph loader:
##### Single subgraph
```
import earlgrey.thegraph.thegraph_loader as gl
data = gl.load_subgraph(<subgraph_url>, <subgraph_query>)
```
#### Multiple subgraphs
```
import earlgrey.thegraph.thegraph_loader as gl
data = gl.load_subgraphs([gl.SubgraphDef(url=<subgraph_url1>, query=<subgraph_query1>), gl.SubgraphDef(url=<subgraph_url2>,query=<subgraph_query2>)])
```

### Run Earlgrey
`earlgrey run <app_file.py>`