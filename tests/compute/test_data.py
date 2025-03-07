import unittest
import backend as F
import numpy as np
import gzip
import tempfile
import os
import pandas as pd
import yaml
import pytest
import dgl.data as data
from dgl import DGLError
import dgl

@unittest.skipIf(F._default_context_str == 'gpu', reason="Datasets don't need to be tested on GPU.")
def test_minigc():
    ds = data.MiniGCDataset(16, 10, 20)
    g, l = list(zip(*ds))
    print(g, l)


@unittest.skipIf(F._default_context_str == 'gpu', reason="Datasets don't need to be tested on GPU.")
def test_gin():
    ds_n_graphs = {
        'MUTAG': 188,
        'IMDBBINARY': 1000,
        'IMDBMULTI': 1500,
        'PROTEINS': 1113,
        'PTC': 344,
    }
    for name, n_graphs in ds_n_graphs.items():
        ds = data.GINDataset(name, self_loop=False, degree_as_nlabel=False)
        assert len(ds) == n_graphs, (len(ds), name)


@unittest.skipIf(F._default_context_str == 'gpu', reason="Datasets don't need to be tested on GPU.")
def test_fraud():
    g = data.FraudDataset('amazon')[0]
    assert g.num_nodes() == 11944

    g = data.FraudAmazonDataset()[0]
    assert g.num_nodes() == 11944

    g = data.FraudYelpDataset()[0]
    assert g.num_nodes() == 45954


@unittest.skipIf(F._default_context_str == 'gpu', reason="Datasets don't need to be tested on GPU.")
def test_fakenews():
    ds = data.FakeNewsDataset('politifact', 'bert')
    assert len(ds) == 314

    ds = data.FakeNewsDataset('gossipcop', 'profile')
    assert len(ds) == 5464


@unittest.skipIf(F._default_context_str == 'gpu', reason="Datasets don't need to be tested on GPU.")
def test_tudataset_regression():
    ds = data.TUDataset('ZINC_test', force_reload=True)
    assert len(ds) == 5000


@unittest.skipIf(F._default_context_str == 'gpu', reason="Datasets don't need to be tested on GPU.")
def test_data_hash():
    class HashTestDataset(data.DGLDataset):
        def __init__(self, hash_key=()):
            super(HashTestDataset, self).__init__(
                'hashtest', hash_key=hash_key)

        def _load(self):
            pass

    a = HashTestDataset((True, 0, '1', (1, 2, 3)))
    b = HashTestDataset((True, 0, '1', (1, 2, 3)))
    c = HashTestDataset((True, 0, '1', (1, 2, 4)))
    assert a.hash == b.hash
    assert a.hash != c.hash


@unittest.skipIf(F._default_context_str == 'gpu', reason="Datasets don't need to be tested on GPU.")
def test_citation_graph():
    # cora
    g = data.CoraGraphDataset()[0]
    assert g.num_nodes() == 2708
    assert g.num_edges() == 10556
    dst = F.asnumpy(g.edges()[1])
    assert np.array_equal(dst, np.sort(dst))

    # Citeseer
    g = data.CiteseerGraphDataset()[0]
    assert g.num_nodes() == 3327
    assert g.num_edges() == 9228
    dst = F.asnumpy(g.edges()[1])
    assert np.array_equal(dst, np.sort(dst))

    # Pubmed
    g = data.PubmedGraphDataset()[0]
    assert g.num_nodes() == 19717
    assert g.num_edges() == 88651
    dst = F.asnumpy(g.edges()[1])
    assert np.array_equal(dst, np.sort(dst))


@unittest.skipIf(F._default_context_str == 'gpu', reason="Datasets don't need to be tested on GPU.")
def test_gnn_benchmark():
    # AmazonCoBuyComputerDataset
    g = data.AmazonCoBuyComputerDataset()[0]
    assert g.num_nodes() == 13752
    assert g.num_edges() == 491722
    dst = F.asnumpy(g.edges()[1])
    assert np.array_equal(dst, np.sort(dst))

    # AmazonCoBuyPhotoDataset
    g = data.AmazonCoBuyPhotoDataset()[0]
    assert g.num_nodes() == 7650
    assert g.num_edges() == 238163
    dst = F.asnumpy(g.edges()[1])
    assert np.array_equal(dst, np.sort(dst))

    # CoauthorPhysicsDataset
    g = data.CoauthorPhysicsDataset()[0]
    assert g.num_nodes() == 34493
    assert g.num_edges() == 495924
    dst = F.asnumpy(g.edges()[1])
    assert np.array_equal(dst, np.sort(dst))

    # CoauthorCSDataset
    g = data.CoauthorCSDataset()[0]
    assert g.num_nodes() == 18333
    assert g.num_edges() == 163788
    dst = F.asnumpy(g.edges()[1])
    assert np.array_equal(dst, np.sort(dst))

    # CoraFullDataset
    g = data.CoraFullDataset()[0]
    assert g.num_nodes() == 19793
    assert g.num_edges() == 126842
    dst = F.asnumpy(g.edges()[1])
    assert np.array_equal(dst, np.sort(dst))


@unittest.skipIf(F._default_context_str == 'gpu', reason="Datasets don't need to be tested on GPU.")
def test_reddit():
    # RedditDataset
    g = data.RedditDataset()[0]
    assert g.num_nodes() == 232965
    assert g.num_edges() == 114615892
    dst = F.asnumpy(g.edges()[1])
    assert np.array_equal(dst, np.sort(dst))


@unittest.skipIf(F._default_context_str == 'gpu', reason="Datasets don't need to be tested on GPU.")
def test_extract_archive():
    # gzip
    with tempfile.TemporaryDirectory() as src_dir:
        gz_file = 'gz_archive'
        gz_path = os.path.join(src_dir, gz_file + '.gz')
        content = b"test extract archive gzip"
        with gzip.open(gz_path, 'wb') as f:
            f.write(content)
        with tempfile.TemporaryDirectory() as dst_dir:
            data.utils.extract_archive(gz_path, dst_dir, overwrite=True)
            assert os.path.exists(os.path.join(dst_dir, gz_file))


def _test_construct_graphs_homo():
    from dgl.data.csv_dataset_base import NodeData, EdgeData, DGLGraphConstructor
    # node_ids could be non-sorted, duplicated, not labeled from 0 to num_nodes-1
    num_nodes = 100
    num_edges = 1000
    num_dims = 3
    num_dup_nodes = int(num_nodes*0.2)
    node_ids = np.random.choice(
        np.arange(num_nodes*2), size=num_nodes, replace=False)
    assert len(node_ids) == num_nodes
    np.random.shuffle(node_ids)
    node_ids = np.hstack((node_ids, node_ids[:num_dup_nodes]))
    t_ndata = {'feat': np.random.rand(num_nodes+num_dup_nodes, num_dims),
               'label': np.random.randint(2, size=num_nodes+num_dup_nodes)}
    _, u_indices = np.unique(node_ids, return_index=True)
    ndata = {'feat': t_ndata['feat'][u_indices],
             'label': t_ndata['label'][u_indices]}
    node_data = NodeData(node_ids, t_ndata)
    src_ids = np.random.choice(node_ids, size=num_edges)
    dst_ids = np.random.choice(node_ids, size=num_edges)
    edata = {'feat': np.random.rand(
        num_edges, num_dims), 'label': np.random.randint(2, size=num_edges)}
    edge_data = EdgeData(src_ids, dst_ids, edata)
    graphs, data_dict = DGLGraphConstructor.construct_graphs(
        node_data, edge_data)
    assert len(graphs) == 1
    assert len(data_dict) == 0
    g = graphs[0]
    assert g.is_homogeneous
    assert g.num_nodes() == num_nodes
    assert g.num_edges() == num_edges

    def assert_data(lhs, rhs):
        for key, value in lhs.items():
            assert key in rhs
            assert F.array_equal(F.tensor(value), rhs[key])
    assert_data(ndata, g.ndata)
    assert_data(edata, g.edata)


def _test_construct_graphs_hetero():
    from dgl.data.csv_dataset_base import NodeData, EdgeData, DGLGraphConstructor
    # node_ids could be non-sorted, duplicated, not labeled from 0 to num_nodes-1
    num_nodes = 100
    num_edges = 1000
    num_dims = 3
    num_dup_nodes = int(num_nodes*0.2)
    ntypes = ['user', 'item']
    node_data = []
    node_ids_dict = {}
    ndata_dict = {}
    for ntype in ntypes:
        node_ids = np.random.choice(
            np.arange(num_nodes*2), size=num_nodes, replace=False)
        assert len(node_ids) == num_nodes
        np.random.shuffle(node_ids)
        node_ids = np.hstack((node_ids, node_ids[:num_dup_nodes]))
        t_ndata = {'feat': np.random.rand(num_nodes+num_dup_nodes, num_dims),
                   'label': np.random.randint(2, size=num_nodes+num_dup_nodes)}
        _, u_indices = np.unique(node_ids, return_index=True)
        ndata = {'feat': t_ndata['feat'][u_indices],
                 'label': t_ndata['label'][u_indices]}
        node_data.append(NodeData(node_ids, t_ndata, type=ntype))
        node_ids_dict[ntype] = node_ids
        ndata_dict[ntype] = ndata
    etypes = [('user', 'follow', 'user'), ('user', 'like', 'item')]
    edge_data = []
    edata_dict = {}
    for src_type, e_type, dst_type in etypes:
        src_ids = np.random.choice(node_ids_dict[src_type], size=num_edges)
        dst_ids = np.random.choice(node_ids_dict[dst_type], size=num_edges)
        edata = {'feat': np.random.rand(
            num_edges, num_dims), 'label': np.random.randint(2, size=num_edges)}
        edge_data.append(EdgeData(src_ids, dst_ids, edata,
                         type=(src_type, e_type, dst_type)))
        edata_dict[(src_type, e_type, dst_type)] = edata
    graphs, data_dict = DGLGraphConstructor.construct_graphs(
        node_data, edge_data)
    assert len(graphs) == 1
    assert len(data_dict) == 0
    g = graphs[0]
    assert not g.is_homogeneous
    assert g.num_nodes() == num_nodes*len(ntypes)
    assert g.num_edges() == num_edges*len(etypes)

    def assert_data(lhs, rhs):
        for key, value in lhs.items():
            assert key in rhs
            assert F.array_equal(F.tensor(value), rhs[key])
    for ntype in g.ntypes:
        assert g.num_nodes(ntype) == num_nodes
        assert_data(ndata_dict[ntype], g.nodes[ntype].data)
    for etype in g.canonical_etypes:
        assert g.num_edges(etype) == num_edges
        assert_data(edata_dict[etype], g.edges[etype].data)


def _test_construct_graphs_multiple():
    from dgl.data.csv_dataset_base import NodeData, EdgeData, GraphData, DGLGraphConstructor
    num_nodes = 100
    num_edges = 1000
    num_graphs = 10
    num_dims = 3
    node_ids = np.array([], dtype=np.int)
    src_ids = np.array([], dtype=np.int)
    dst_ids = np.array([], dtype=np.int)
    ngraph_ids = np.array([], dtype=np.int)
    egraph_ids = np.array([], dtype=np.int)
    u_indices = np.array([], dtype=np.int)
    for i in range(num_graphs):
        l_node_ids = np.random.choice(
            np.arange(num_nodes*2), size=num_nodes, replace=False)
        node_ids = np.append(node_ids, l_node_ids)
        _, l_u_indices = np.unique(l_node_ids, return_index=True)
        u_indices = np.append(u_indices, l_u_indices)
        ngraph_ids = np.append(ngraph_ids, np.full(num_nodes, i))
        src_ids = np.append(src_ids, np.random.choice(
            l_node_ids, size=num_edges))
        dst_ids = np.append(dst_ids, np.random.choice(
            l_node_ids, size=num_edges))
        egraph_ids = np.append(egraph_ids, np.full(num_edges, i))
    ndata = {'feat': np.random.rand(num_nodes*num_graphs, num_dims),
             'label': np.random.randint(2, size=num_nodes*num_graphs)}
    node_data = NodeData(node_ids, ndata, graph_id=ngraph_ids)
    edata = {'feat': np.random.rand(
        num_edges*num_graphs, num_dims), 'label': np.random.randint(2, size=num_edges*num_graphs)}
    edge_data = EdgeData(src_ids, dst_ids, edata, graph_id=egraph_ids)
    gdata = {'feat': np.random.rand(num_graphs, num_dims),
             'label': np.random.randint(2, size=num_graphs)}
    graph_data = GraphData(np.arange(num_graphs), gdata)
    graphs, data_dict = DGLGraphConstructor.construct_graphs(
        node_data, edge_data, graph_data)
    assert len(graphs) == num_graphs
    assert len(data_dict) == len(gdata)
    for k, v in data_dict.items():
        assert F.array_equal(F.tensor(gdata[k]), v)
    for i, g in enumerate(graphs):
        assert g.is_homogeneous
        assert g.num_nodes() == num_nodes
        assert g.num_edges() == num_edges

        def assert_data(lhs, rhs, size, node=False):
            for key, value in lhs.items():
                assert key in rhs
                value = value[i*size:(i+1)*size]
                if node:
                    indices = u_indices[i*size:(i+1)*size]
                    value = value[indices]
                assert F.array_equal(F.tensor(value), rhs[key])
        assert_data(ndata, g.ndata, num_nodes, node=True)
        assert_data(edata, g.edata, num_edges)

    # Graph IDs found in node/edge CSV but not in graph CSV
    graph_data = GraphData(np.arange(num_graphs-2), {})
    expect_except = False
    try:
        _, _ = DGLGraphConstructor.construct_graphs(
            node_data, edge_data, graph_data)
    except:
        expect_except = True
    assert expect_except


def _test_DefaultDataParser():
    from dgl.data.csv_dataset_base import DefaultDataParser
    # common csv
    with tempfile.TemporaryDirectory() as test_dir:
        csv_path = os.path.join(test_dir, "nodes.csv")
        num_nodes = 5
        num_labels = 3
        num_dims = 2
        node_id = np.arange(num_nodes)
        label = np.random.randint(num_labels, size=num_nodes)
        feat = np.random.rand(num_nodes, num_dims)
        df = pd.DataFrame({'node_id': node_id, 'label': label,
                           'feat': [line.tolist() for line in feat],
                           })
        df.to_csv(csv_path, index=False)
        dp = DefaultDataParser()
        df = pd.read_csv(csv_path)
        dt = dp(df)
        assert np.array_equal(node_id, dt['node_id'])
        assert np.array_equal(label, dt['label'])
        assert np.array_equal(feat, dt['feat'])
    # string consists of non-numeric values
    with tempfile.TemporaryDirectory() as test_dir:
        csv_path = os.path.join(test_dir, "nodes.csv")
        df = pd.DataFrame({'label': ['a', 'b', 'c'],
                           })
        df.to_csv(csv_path, index=False)
        dp = DefaultDataParser()
        df = pd.read_csv(csv_path)
        expect_except = False
        try:
            dt = dp(df)
        except:
            expect_except = True
        assert expect_except
    # csv has index column which is ignored as it's unnamed
    with tempfile.TemporaryDirectory() as test_dir:
        csv_path = os.path.join(test_dir, "nodes.csv")
        df = pd.DataFrame({'label': [1, 2, 3],
                           })
        df.to_csv(csv_path)
        dp = DefaultDataParser()
        df = pd.read_csv(csv_path)
        dt = dp(df)
        assert len(dt) == 1


def _test_load_yaml_with_sanity_check():
    from dgl.data.csv_dataset_base import load_yaml_with_sanity_check
    with tempfile.TemporaryDirectory() as test_dir:
        yaml_path = os.path.join(test_dir, 'meta.yaml')
        # workable but meaningless usually
        yaml_data = {'dataset_name': 'default',
                     'node_data': [], 'edge_data': []}
        with open(yaml_path, 'w') as f:
            yaml.dump(yaml_data, f, sort_keys=False)
        meta = load_yaml_with_sanity_check(yaml_path)
        assert meta.version == '1.0.0'
        assert meta.dataset_name == 'default'
        assert meta.separator == ','
        assert len(meta.node_data) == 0
        assert len(meta.edge_data) == 0
        assert meta.graph_data is None
        # minimum with required fields only
        yaml_data = {'version': '1.0.0', 'dataset_name': 'default', 'node_data': [{'file_name': 'nodes.csv'}],
                     'edge_data': [{'file_name': 'edges.csv'}],
                     }
        with open(yaml_path, 'w') as f:
            yaml.dump(yaml_data, f, sort_keys=False)
        meta = load_yaml_with_sanity_check(yaml_path)
        for ndata in meta.node_data:
            assert ndata.file_name == 'nodes.csv'
            assert ndata.ntype == '_V'
            assert ndata.graph_id_field == 'graph_id'
            assert ndata.node_id_field == 'node_id'
        for edata in meta.edge_data:
            assert edata.file_name == 'edges.csv'
            assert edata.etype == ['_V', '_E', '_V']
            assert edata.graph_id_field == 'graph_id'
            assert edata.src_id_field == 'src_id'
            assert edata.dst_id_field == 'dst_id'
        # optional fields are specified
        yaml_data = {'version': '1.0.0', 'dataset_name': 'default',
                     'separator': '|',
                     'node_data': [{'file_name': 'nodes.csv', 'ntype': 'user', 'graph_id_field': 'xxx', 'node_id_field': 'xxx'}],
                     'edge_data': [{'file_name': 'edges.csv', 'etype': ['user', 'follow', 'user'], 'graph_id_field':'xxx', 'src_id_field':'xxx', 'dst_id_field':'xxx'}],
                     'graph_data': {'file_name': 'graph.csv', 'graph_id_field': 'xxx'}
                     }
        with open(yaml_path, 'w') as f:
            yaml.dump(yaml_data, f, sort_keys=False)
        meta = load_yaml_with_sanity_check(yaml_path)
        assert len(meta.node_data) == 1
        ndata = meta.node_data[0]
        assert ndata.ntype == 'user'
        assert ndata.graph_id_field == 'xxx'
        assert ndata.node_id_field == 'xxx'
        assert len(meta.edge_data) == 1
        edata = meta.edge_data[0]
        assert edata.etype == ['user', 'follow', 'user']
        assert edata.graph_id_field == 'xxx'
        assert edata.src_id_field == 'xxx'
        assert edata.dst_id_field == 'xxx'
        assert meta.graph_data is not None
        assert meta.graph_data.file_name == 'graph.csv'
        assert meta.graph_data.graph_id_field == 'xxx'
        # some required fields are missing
        yaml_data = {'dataset_name': 'default',
                     'node_data': [], 'edge_data': []}
        for field in yaml_data.keys():
            ydata = {k: v for k, v in yaml_data.items()}
            ydata.pop(field)
            with open(yaml_path, 'w') as f:
                yaml.dump(ydata, f, sort_keys=False)
            expect_except = False
            try:
                meta = load_yaml_with_sanity_check(yaml_path)
            except:
                expect_except = True
            assert expect_except
        # inapplicable version
        yaml_data = {'version': '0.0.0', 'dataset_name': 'default', 'node_data': [{'file_name': 'nodes_0.csv'}],
                     'edge_data': [{'file_name': 'edges_0.csv'}],
                     }
        with open(yaml_path, 'w') as f:
            yaml.dump(yaml_data, f, sort_keys=False)
        expect_except = False
        try:
            meta = load_yaml_with_sanity_check(yaml_path)
        except DGLError:
            expect_except = True
        assert expect_except
        # duplicate node types
        yaml_data = {'version': '1.0.0', 'dataset_name': 'default', 'node_data': [{'file_name': 'nodes.csv'}, {'file_name': 'nodes.csv'}],
                     'edge_data': [{'file_name': 'edges.csv'}],
                     }
        with open(yaml_path, 'w') as f:
            yaml.dump(yaml_data, f, sort_keys=False)
        expect_except = False
        try:
            meta = load_yaml_with_sanity_check(yaml_path)
        except DGLError:
            expect_except = True
        assert expect_except
        # duplicate edge types
        yaml_data = {'version': '1.0.0', 'dataset_name': 'default', 'node_data': [{'file_name': 'nodes.csv'}],
                     'edge_data': [{'file_name': 'edges.csv'}, {'file_name': 'edges.csv'}],
                     }
        with open(yaml_path, 'w') as f:
            yaml.dump(yaml_data, f, sort_keys=False)
        expect_except = False
        try:
            meta = load_yaml_with_sanity_check(yaml_path)
        except DGLError:
            expect_except = True
        assert expect_except


def _test_load_node_data_from_csv():
    from dgl.data.csv_dataset_base import MetaNode, NodeData, DefaultDataParser
    with tempfile.TemporaryDirectory() as test_dir:
        num_nodes = 100
        # minimum
        df = pd.DataFrame({'node_id': np.arange(num_nodes)})
        csv_path = os.path.join(test_dir, 'nodes.csv')
        df.to_csv(csv_path, index=False)
        meta_node = MetaNode(file_name=csv_path)
        node_data = NodeData.load_from_csv(
            meta_node, DefaultDataParser())
        assert np.array_equal(df['node_id'], node_data.id)
        assert len(node_data.data) == 0

        # common case
        df = pd.DataFrame({'node_id': np.arange(num_nodes),
                          'label': np.random.randint(3, size=num_nodes)})
        csv_path = os.path.join(test_dir, 'nodes.csv')
        df.to_csv(csv_path, index=False)
        meta_node = MetaNode(file_name=csv_path)
        node_data = NodeData.load_from_csv(
            meta_node, DefaultDataParser())
        assert np.array_equal(df['node_id'], node_data.id)
        assert len(node_data.data) == 1
        assert np.array_equal(df['label'], node_data.data['label'])
        assert np.array_equal(np.full(num_nodes, 0), node_data.graph_id)
        assert node_data.type == '_V'

        # add more fields into nodes.csv
        df = pd.DataFrame({'node_id': np.arange(num_nodes), 'label': np.random.randint(
            3, size=num_nodes), 'graph_id': np.full(num_nodes, 1)})
        csv_path = os.path.join(test_dir, 'nodes.csv')
        df.to_csv(csv_path, index=False)
        meta_node = MetaNode(file_name=csv_path)
        node_data = NodeData.load_from_csv(
            meta_node, DefaultDataParser())
        assert np.array_equal(df['node_id'], node_data.id)
        assert len(node_data.data) == 1
        assert np.array_equal(df['label'], node_data.data['label'])
        assert np.array_equal(df['graph_id'], node_data.graph_id)
        assert node_data.type == '_V'

        # required header is missing
        df = pd.DataFrame({'label': np.random.randint(3, size=num_nodes)})
        csv_path = os.path.join(test_dir, 'nodes.csv')
        df.to_csv(csv_path, index=False)
        meta_node = MetaNode(file_name=csv_path)
        expect_except = False
        try:
            NodeData.load_from_csv(
                meta_node, DefaultDataParser())
        except:
            expect_except = True
        assert expect_except


def _test_load_edge_data_from_csv():
    from dgl.data.csv_dataset_base import MetaEdge, EdgeData, DefaultDataParser
    with tempfile.TemporaryDirectory() as test_dir:
        num_nodes = 100
        num_edges = 1000
        # minimum
        df = pd.DataFrame({'src_id': np.random.randint(num_nodes, size=num_edges),
                           'dst_id': np.random.randint(num_nodes, size=num_edges),
                           })
        csv_path = os.path.join(test_dir, 'edges.csv')
        df.to_csv(csv_path, index=False)
        meta_edge = MetaEdge(file_name=csv_path)
        edge_data = EdgeData.load_from_csv(
            meta_edge, DefaultDataParser())
        assert np.array_equal(df['src_id'], edge_data.src)
        assert np.array_equal(df['dst_id'], edge_data.dst)
        assert len(edge_data.data) == 0

        # common case
        df = pd.DataFrame({'src_id': np.random.randint(num_nodes, size=num_edges),
                           'dst_id': np.random.randint(num_nodes, size=num_edges),
                           'label': np.random.randint(3, size=num_edges)})
        csv_path = os.path.join(test_dir, 'edges.csv')
        df.to_csv(csv_path, index=False)
        meta_edge = MetaEdge(file_name=csv_path)
        edge_data = EdgeData.load_from_csv(
            meta_edge, DefaultDataParser())
        assert np.array_equal(df['src_id'], edge_data.src)
        assert np.array_equal(df['dst_id'], edge_data.dst)
        assert len(edge_data.data) == 1
        assert np.array_equal(df['label'], edge_data.data['label'])
        assert np.array_equal(np.full(num_edges, 0), edge_data.graph_id)
        assert edge_data.type == ('_V', '_E', '_V')

        # add more fields into edges.csv
        df = pd.DataFrame({'src_id': np.random.randint(num_nodes, size=num_edges),
                           'dst_id': np.random.randint(num_nodes, size=num_edges),
                           'graph_id': np.arange(num_edges),
                           'feat': np.random.randint(3, size=num_edges),
                           'label': np.random.randint(3, size=num_edges)})
        csv_path = os.path.join(test_dir, 'edges.csv')
        df.to_csv(csv_path, index=False)
        meta_edge = MetaEdge(file_name=csv_path)
        edge_data = EdgeData.load_from_csv(
            meta_edge, DefaultDataParser())
        assert np.array_equal(df['src_id'], edge_data.src)
        assert np.array_equal(df['dst_id'], edge_data.dst)
        assert len(edge_data.data) == 2
        assert np.array_equal(df['feat'], edge_data.data['feat'])
        assert np.array_equal(df['label'], edge_data.data['label'])
        assert np.array_equal(df['graph_id'], edge_data.graph_id)
        assert edge_data.type == ('_V', '_E', '_V')

        # required headers are missing
        df = pd.DataFrame({'src_id': np.random.randint(num_nodes, size=num_edges),
                           })
        csv_path = os.path.join(test_dir, 'edges.csv')
        df.to_csv(csv_path, index=False)
        meta_edge = MetaEdge(file_name=csv_path)
        expect_except = False
        try:
            EdgeData.load_from_csv(
                meta_edge, DefaultDataParser())
        except DGLError:
            expect_except = True
        assert expect_except
        df = pd.DataFrame({'dst_id': np.random.randint(num_nodes, size=num_edges),
                           })
        csv_path = os.path.join(test_dir, 'edges.csv')
        df.to_csv(csv_path, index=False)
        meta_edge = MetaEdge(file_name=csv_path)
        expect_except = False
        try:
            EdgeData.load_from_csv(
                meta_edge, DefaultDataParser())
        except DGLError:
            expect_except = True
        assert expect_except


def _test_load_graph_data_from_csv():
    from dgl.data.csv_dataset_base import MetaGraph, GraphData, DefaultDataParser
    with tempfile.TemporaryDirectory() as test_dir:
        num_graphs = 100
        # minimum
        df = pd.DataFrame({'graph_id': np.arange(num_graphs)})
        csv_path = os.path.join(test_dir, 'graph.csv')
        df.to_csv(csv_path, index=False)
        meta_graph = MetaGraph(file_name=csv_path)
        graph_data = GraphData.load_from_csv(
            meta_graph, DefaultDataParser())
        assert np.array_equal(df['graph_id'], graph_data.graph_id)
        assert len(graph_data.data) == 0

        # common case
        df = pd.DataFrame({'graph_id': np.arange(num_graphs),
                          'label': np.random.randint(3, size=num_graphs)})
        csv_path = os.path.join(test_dir, 'graph.csv')
        df.to_csv(csv_path, index=False)
        meta_graph = MetaGraph(file_name=csv_path)
        graph_data = GraphData.load_from_csv(
            meta_graph, DefaultDataParser())
        assert np.array_equal(df['graph_id'], graph_data.graph_id)
        assert len(graph_data.data) == 1
        assert np.array_equal(df['label'], graph_data.data['label'])

        # add more fields into graph.csv
        df = pd.DataFrame({'graph_id': np.arange(num_graphs),
                           'feat': np.random.randint(3, size=num_graphs),
                           'label': np.random.randint(3, size=num_graphs)})
        csv_path = os.path.join(test_dir, 'graph.csv')
        df.to_csv(csv_path, index=False)
        meta_graph = MetaGraph(file_name=csv_path)
        graph_data = GraphData.load_from_csv(
            meta_graph, DefaultDataParser())
        assert np.array_equal(df['graph_id'], graph_data.graph_id)
        assert len(graph_data.data) == 2
        assert np.array_equal(df['feat'], graph_data.data['feat'])
        assert np.array_equal(df['label'], graph_data.data['label'])

        # required header is missing
        df = pd.DataFrame({'label': np.random.randint(3, size=num_graphs)})
        csv_path = os.path.join(test_dir, 'graph.csv')
        df.to_csv(csv_path, index=False)
        meta_graph = MetaGraph(file_name=csv_path)
        expect_except = False
        try:
            GraphData.load_from_csv(
                meta_graph, DefaultDataParser())
        except DGLError:
            expect_except = True
        assert expect_except


def _test_DGLCSVDataset_single():
    with tempfile.TemporaryDirectory() as test_dir:
        # generate YAML/CSVs
        meta_yaml_path = os.path.join(test_dir, "meta.yaml")
        edges_csv_path_0 = os.path.join(test_dir, "test_edges_0.csv")
        edges_csv_path_1 = os.path.join(test_dir, "test_edges_1.csv")
        nodes_csv_path_0 = os.path.join(test_dir, "test_nodes_0.csv")
        nodes_csv_path_1 = os.path.join(test_dir, "test_nodes_1.csv")
        meta_yaml_data = {'version': '1.0.0', 'dataset_name': 'default_name',
                          'node_data': [{'file_name': os.path.basename(nodes_csv_path_0),
                                         'ntype': 'user',
                                         },
                                        {'file_name': os.path.basename(nodes_csv_path_1),
                                            'ntype': 'item',
                                         }],
                          'edge_data': [{'file_name': os.path.basename(edges_csv_path_0),
                                         'etype': ['user', 'follow', 'user'],
                                         },
                                        {'file_name': os.path.basename(edges_csv_path_1),
                                         'etype': ['user', 'like', 'item'],
                                         }],
                          }
        with open(meta_yaml_path, 'w') as f:
            yaml.dump(meta_yaml_data, f, sort_keys=False)
        num_nodes = 100
        num_edges = 500
        num_dims = 3
        feat_ndata = np.random.rand(num_nodes, num_dims)
        label_ndata = np.random.randint(2, size=num_nodes)
        df = pd.DataFrame({'node_id': np.arange(num_nodes),
                           'label': label_ndata,
                           'feat': [line.tolist() for line in feat_ndata],
                           })
        df.to_csv(nodes_csv_path_0, index=False)
        df.to_csv(nodes_csv_path_1, index=False)
        feat_edata = np.random.rand(num_edges, num_dims)
        label_edata = np.random.randint(2, size=num_edges)
        df = pd.DataFrame({'src_id': np.random.randint(num_nodes, size=num_edges),
                           'dst_id': np.random.randint(num_nodes, size=num_edges),
                           'label': label_edata,
                           'feat': [line.tolist() for line in feat_edata],
                           })
        df.to_csv(edges_csv_path_0, index=False)
        df.to_csv(edges_csv_path_1, index=False)

        # load CSVDataset
        for force_reload in [True, False]:
            if not force_reload:
                # remove original node data file to verify reload from cached files
                os.remove(nodes_csv_path_0)
                assert not os.path.exists(nodes_csv_path_0)
            csv_dataset = data.DGLCSVDataset(
                test_dir, force_reload=force_reload)
            assert len(csv_dataset) == 1
            g = csv_dataset[0]
            assert not g.is_homogeneous
            assert csv_dataset.has_cache()
            for ntype in g.ntypes:
                assert g.num_nodes(ntype) == num_nodes
                assert F.array_equal(F.tensor(feat_ndata),
                                     g.nodes[ntype].data['feat'])
                assert np.array_equal(label_ndata,
                                      F.asnumpy(g.nodes[ntype].data['label']))
            for etype in g.etypes:
                assert g.num_edges(etype) == num_edges
                assert F.array_equal(F.tensor(feat_edata),
                                     g.edges[etype].data['feat'])
                assert np.array_equal(label_edata,
                                      F.asnumpy(g.edges[etype].data['label']))


def _test_DGLCSVDataset_multiple():
    with tempfile.TemporaryDirectory() as test_dir:
        # generate YAML/CSVs
        meta_yaml_path = os.path.join(test_dir, "meta.yaml")
        edges_csv_path_0 = os.path.join(test_dir, "test_edges_0.csv")
        edges_csv_path_1 = os.path.join(test_dir, "test_edges_1.csv")
        nodes_csv_path_0 = os.path.join(test_dir, "test_nodes_0.csv")
        nodes_csv_path_1 = os.path.join(test_dir, "test_nodes_1.csv")
        graph_csv_path = os.path.join(test_dir, "test_graph.csv")
        meta_yaml_data = {'version': '1.0.0', 'dataset_name': 'default_name',
                          'node_data': [{'file_name': os.path.basename(nodes_csv_path_0),
                                         'ntype': 'user',
                                         },
                                        {'file_name': os.path.basename(nodes_csv_path_1),
                                            'ntype': 'item',
                                         }],
                          'edge_data': [{'file_name': os.path.basename(edges_csv_path_0),
                                         'etype': ['user', 'follow', 'user'],
                                         },
                                        {'file_name': os.path.basename(edges_csv_path_1),
                                         'etype': ['user', 'like', 'item'],
                                         }],
                          'graph_data': {'file_name': os.path.basename(graph_csv_path)}
                          }
        with open(meta_yaml_path, 'w') as f:
            yaml.dump(meta_yaml_data, f, sort_keys=False)
        num_nodes = 100
        num_edges = 500
        num_graphs = 10
        num_dims = 3
        feat_ndata = np.random.rand(num_nodes*num_graphs, num_dims)
        label_ndata = np.random.randint(2, size=num_nodes*num_graphs)
        df = pd.DataFrame({'node_id': np.hstack([np.arange(num_nodes) for _ in range(num_graphs)]),
                           'label': label_ndata,
                           'feat': [line.tolist() for line in feat_ndata],
                           'graph_id': np.hstack([np.full(num_nodes, i) for i in range(num_graphs)])
                           })
        df.to_csv(nodes_csv_path_0, index=False)
        df.to_csv(nodes_csv_path_1, index=False)
        feat_edata = np.random.rand(num_edges*num_graphs, num_dims)
        label_edata = np.random.randint(2, size=num_edges*num_graphs)
        df = pd.DataFrame({'src_id': np.hstack([np.random.randint(num_nodes, size=num_edges) for _ in range(num_graphs)]),
                           'dst_id': np.hstack([np.random.randint(num_nodes, size=num_edges) for _ in range(num_graphs)]),
                           'label': label_edata,
                           'feat': [line.tolist() for line in feat_edata],
                           'graph_id': np.hstack([np.full(num_edges, i) for i in range(num_graphs)])
                           })
        df.to_csv(edges_csv_path_0, index=False)
        df.to_csv(edges_csv_path_1, index=False)
        feat_gdata = np.random.rand(num_graphs, num_dims)
        label_gdata = np.random.randint(2, size=num_graphs)
        df = pd.DataFrame({'label': label_gdata,
                           'feat': [line.tolist() for line in feat_gdata],
                           'graph_id': np.arange(num_graphs)
                           })
        df.to_csv(graph_csv_path, index=False)

        # load CSVDataset with default node/edge/graph_data_parser
        for force_reload in [True, False]:
            if not force_reload:
                # remove original node data file to verify reload from cached files
                os.remove(nodes_csv_path_0)
                assert not os.path.exists(nodes_csv_path_0)
            csv_dataset = data.DGLCSVDataset(
                test_dir, force_reload=force_reload)
            assert len(csv_dataset) == num_graphs
            assert csv_dataset.has_cache()
            assert len(csv_dataset.data) == 2
            assert 'feat' in csv_dataset.data
            assert 'label' in csv_dataset.data
            assert F.array_equal(F.tensor(feat_gdata),
                                 csv_dataset.data['feat'])
            for i, (g, label) in enumerate(csv_dataset):
                assert not g.is_homogeneous
                assert F.asnumpy(label) == label_gdata[i]
                for ntype in g.ntypes:
                    assert g.num_nodes(ntype) == num_nodes
                    assert F.array_equal(F.tensor(feat_ndata[i*num_nodes:(i+1)*num_nodes]),
                                         g.nodes[ntype].data['feat'])
                    assert np.array_equal(label_ndata[i*num_nodes:(i+1)*num_nodes],
                                          F.asnumpy(g.nodes[ntype].data['label']))
                for etype in g.etypes:
                    assert g.num_edges(etype) == num_edges
                    assert F.array_equal(F.tensor(feat_edata[i*num_edges:(i+1)*num_edges]),
                                         g.edges[etype].data['feat'])
                    assert np.array_equal(label_edata[i*num_edges:(i+1)*num_edges],
                                          F.asnumpy(g.edges[etype].data['label']))


def _test_DGLCSVDataset_customized_data_parser():
    with tempfile.TemporaryDirectory() as test_dir:
        # generate YAML/CSVs
        meta_yaml_path = os.path.join(test_dir, "meta.yaml")
        edges_csv_path_0 = os.path.join(test_dir, "test_edges_0.csv")
        edges_csv_path_1 = os.path.join(test_dir, "test_edges_1.csv")
        nodes_csv_path_0 = os.path.join(test_dir, "test_nodes_0.csv")
        nodes_csv_path_1 = os.path.join(test_dir, "test_nodes_1.csv")
        graph_csv_path = os.path.join(test_dir, "test_graph.csv")
        meta_yaml_data = {'dataset_name': 'default_name',
                          'node_data': [{'file_name': os.path.basename(nodes_csv_path_0),
                                         'ntype': 'user',
                                         },
                                        {'file_name': os.path.basename(nodes_csv_path_1),
                                            'ntype': 'item',
                                         }],
                          'edge_data': [{'file_name': os.path.basename(edges_csv_path_0),
                                         'etype': ['user', 'follow', 'user'],
                                         },
                                        {'file_name': os.path.basename(edges_csv_path_1),
                                         'etype': ['user', 'like', 'item'],
                                         }],
                          'graph_data': {'file_name': os.path.basename(graph_csv_path)}
                          }
        with open(meta_yaml_path, 'w') as f:
            yaml.dump(meta_yaml_data, f, sort_keys=False)
        num_nodes = 100
        num_edges = 500
        num_graphs = 10
        label_ndata = np.random.randint(2, size=num_nodes*num_graphs)
        df = pd.DataFrame({'node_id': np.hstack([np.arange(num_nodes) for _ in range(num_graphs)]),
                           'label': label_ndata,
                           'graph_id': np.hstack([np.full(num_nodes, i) for i in range(num_graphs)])
                           })
        df.to_csv(nodes_csv_path_0, index=False)
        df.to_csv(nodes_csv_path_1, index=False)
        label_edata = np.random.randint(2, size=num_edges*num_graphs)
        df = pd.DataFrame({'src_id': np.hstack([np.random.randint(num_nodes, size=num_edges) for _ in range(num_graphs)]),
                           'dst_id': np.hstack([np.random.randint(num_nodes, size=num_edges) for _ in range(num_graphs)]),
                           'label': label_edata,
                           'graph_id': np.hstack([np.full(num_edges, i) for i in range(num_graphs)])
                           })
        df.to_csv(edges_csv_path_0, index=False)
        df.to_csv(edges_csv_path_1, index=False)
        label_gdata = np.random.randint(2, size=num_graphs)
        df = pd.DataFrame({'label': label_gdata,
                           'graph_id': np.arange(num_graphs)
                           })
        df.to_csv(graph_csv_path, index=False)

        class CustDataParser:
            def __call__(self, df):
                data = {}
                for header in df:
                    dt = df[header].to_numpy().squeeze()
                    if header == 'label':
                        dt += 2
                    data[header] = dt
                return data
        # load CSVDataset with customized node/edge/graph_data_parser
        csv_dataset = data.DGLCSVDataset(
            test_dir, node_data_parser={'user': CustDataParser()}, edge_data_parser={('user', 'like', 'item'): CustDataParser()}, graph_data_parser=CustDataParser())
        assert len(csv_dataset) == num_graphs
        assert len(csv_dataset.data) == 1
        assert 'label' in csv_dataset.data
        for i, (g, label) in enumerate(csv_dataset):
            assert not g.is_homogeneous
            assert F.asnumpy(label) == label_gdata[i] + 2
            for ntype in g.ntypes:
                assert g.num_nodes(ntype) == num_nodes
                offset = 2 if ntype == 'user' else 0
                assert np.array_equal(label_ndata[i*num_nodes:(i+1)*num_nodes]+offset,
                                      F.asnumpy(g.nodes[ntype].data['label']))
            for etype in g.etypes:
                assert g.num_edges(etype) == num_edges
                offset = 2 if etype == 'like' else 0
                assert np.array_equal(label_edata[i*num_edges:(i+1)*num_edges]+offset,
                                      F.asnumpy(g.edges[etype].data['label']))


def _test_NodeEdgeGraphData():
    from dgl.data.csv_dataset_base import NodeData, EdgeData, GraphData
    # NodeData basics
    num_nodes = 100
    node_ids = np.arange(num_nodes, dtype=np.float)
    ndata = NodeData(node_ids, {})
    assert ndata.id.dtype == np.int64
    assert np.array_equal(ndata.id, node_ids.astype(np.int64))
    assert len(ndata.data) == 0
    assert ndata.type == '_V'
    assert np.array_equal(ndata.graph_id, np.full(num_nodes, 0))
    # NodeData more
    data = {'feat': np.random.rand(num_nodes, 3)}
    graph_id = np.arange(num_nodes)
    ndata = NodeData(node_ids, data, type='user', graph_id=graph_id)
    assert ndata.type == 'user'
    assert np.array_equal(ndata.graph_id, graph_id)
    assert len(ndata.data) == len(data)
    for k, v in data.items():
        assert k in ndata.data
        assert np.array_equal(ndata.data[k], v)
    # NodeData except
    expect_except = False
    try:
        NodeData(np.arange(num_nodes), {'feat': np.random.rand(
            num_nodes+1, 3)}, graph_id=np.arange(num_nodes-1))
    except:
        expect_except = True
    assert expect_except

    # EdgeData basics
    num_nodes = 100
    num_edges = 1000
    src_ids = np.random.randint(num_nodes, size=num_edges)
    dst_ids = np.random.randint(num_nodes, size=num_edges)
    edata = EdgeData(src_ids, dst_ids, {})
    assert np.array_equal(edata.src, src_ids)
    assert np.array_equal(edata.dst, dst_ids)
    assert edata.type == ('_V', '_E', '_V')
    assert len(edata.data) == 0
    assert np.array_equal(edata.graph_id, np.full(num_edges, 0))
    # EdageData more
    src_ids = np.random.randint(num_nodes, size=num_edges).astype(np.float)
    dst_ids = np.random.randint(num_nodes, size=num_edges).astype(np.float)
    data = {'feat': np.random.rand(num_edges, 3)}
    etype = ('user', 'like', 'item')
    graph_ids = np.arange(num_edges)
    edata = EdgeData(src_ids, dst_ids, data,
                            type=etype, graph_id=graph_ids)
    assert edata.src.dtype == np.int64
    assert edata.dst.dtype == np.int64
    assert np.array_equal(edata.src, src_ids)
    assert np.array_equal(edata.dst, dst_ids)
    assert edata.type == etype
    assert len(edata.data) == len(data)
    for k, v in data.items():
        assert k in edata.data
        assert np.array_equal(edata.data[k], v)
    assert np.array_equal(edata.graph_id, graph_ids)
    # EdgeData except
    expect_except = False
    try:
        EdgeData(np.arange(num_edges), np.arange(
            num_edges+1), {'feat': np.random.rand(num_edges-1, 3)}, graph_id=np.arange(num_edges+2))
    except:
        expect_except = True
    assert expect_except

    # GraphData basics
    num_graphs = 10
    graph_ids = np.arange(num_graphs)
    gdata = GraphData(graph_ids, {})
    assert np.array_equal(gdata.graph_id, graph_ids)
    assert len(gdata.data) == 0
    # GraphData more
    graph_ids = np.arange(num_graphs).astype(np.float)
    data = {'feat': np.random.rand(num_graphs, 3)}
    gdata = GraphData(graph_ids, data)
    assert gdata.graph_id.dtype == np.int64
    assert np.array_equal(gdata.graph_id, graph_ids)
    assert len(gdata.data) == len(data)
    for k, v in data.items():
        assert k in gdata.data
        assert np.array_equal(gdata.data[k], v)


@unittest.skipIf(F._default_context_str == 'gpu', reason="Datasets don't need to be tested on GPU.")
def test_csvdataset():
    _test_NodeEdgeGraphData()
    _test_construct_graphs_homo()
    _test_construct_graphs_hetero()
    _test_construct_graphs_multiple()
    _test_DefaultDataParser()
    _test_load_yaml_with_sanity_check()
    _test_load_node_data_from_csv()
    _test_load_edge_data_from_csv()
    _test_load_graph_data_from_csv()
    _test_DGLCSVDataset_single()
    _test_DGLCSVDataset_multiple()
    _test_DGLCSVDataset_customized_data_parser()

@unittest.skipIf(F._default_context_str == 'gpu', reason="Datasets don't need to be tested on GPU.")
def test_add_nodepred_split():
    dataset = data.AmazonCoBuyComputerDataset()
    print('train_mask' in dataset[0].ndata)
    data.utils.add_nodepred_split(dataset, [0.8, 0.1, 0.1])
    assert 'train_mask' in dataset[0].ndata

    dataset = data.AIFBDataset()
    print('train_mask' in dataset[0].nodes['Publikationen'].data)
    data.utils.add_nodepred_split(dataset, [0.8, 0.1, 0.1], ntype='Publikationen')
    assert 'train_mask' in dataset[0].nodes['Publikationen'].data

@unittest.skipIf(F._default_context_str == 'gpu', reason="Datasets don't need to be tested on GPU.")
def test_as_nodepred1():
    ds = data.AmazonCoBuyComputerDataset()
    print('train_mask' in ds[0].ndata)
    new_ds = data.AsNodePredDataset(ds, [0.8, 0.1, 0.1], verbose=True)
    assert len(new_ds) == 1
    assert new_ds[0].num_nodes() == ds[0].num_nodes()
    assert new_ds[0].num_edges() == ds[0].num_edges()
    assert 'train_mask' in new_ds[0].ndata

    ds = data.AIFBDataset()
    print('train_mask' in ds[0].nodes['Personen'].data)
    new_ds = data.AsNodePredDataset(ds, [0.8, 0.1, 0.1], 'Personen', verbose=True)
    assert len(new_ds) == 1
    assert new_ds[0].ntypes == ds[0].ntypes
    assert new_ds[0].canonical_etypes == ds[0].canonical_etypes
    assert 'train_mask' in new_ds[0].nodes['Personen'].data

@unittest.skipIf(F._default_context_str == 'gpu', reason="Datasets don't need to be tested on GPU.")
def test_as_nodepred2():
    # test proper reprocessing

    # create
    ds = data.AsNodePredDataset(data.AmazonCoBuyComputerDataset(), [0.8, 0.1, 0.1])
    assert F.sum(F.astype(ds[0].ndata['train_mask'], F.int32), 0) == int(ds[0].num_nodes() * 0.8)
    # read from cache
    ds = data.AsNodePredDataset(data.AmazonCoBuyComputerDataset(), [0.8, 0.1, 0.1])
    assert F.sum(F.astype(ds[0].ndata['train_mask'], F.int32), 0) == int(ds[0].num_nodes() * 0.8)
    # invalid cache, re-read
    ds = data.AsNodePredDataset(data.AmazonCoBuyComputerDataset(), [0.1, 0.1, 0.8])
    assert F.sum(F.astype(ds[0].ndata['train_mask'], F.int32), 0) == int(ds[0].num_nodes() * 0.1)

    # create
    ds = data.AsNodePredDataset(data.AIFBDataset(), [0.8, 0.1, 0.1], 'Personen', verbose=True)
    assert F.sum(F.astype(ds[0].nodes['Personen'].data['train_mask'], F.int32), 0) == int(ds[0].num_nodes('Personen') * 0.8)
    # read from cache
    ds = data.AsNodePredDataset(data.AIFBDataset(), [0.8, 0.1, 0.1], 'Personen', verbose=True)
    assert F.sum(F.astype(ds[0].nodes['Personen'].data['train_mask'], F.int32), 0) == int(ds[0].num_nodes('Personen') * 0.8)
    # invalid cache, re-read
    ds = data.AsNodePredDataset(data.AIFBDataset(), [0.1, 0.1, 0.8], 'Personen', verbose=True)
    assert F.sum(F.astype(ds[0].nodes['Personen'].data['train_mask'], F.int32), 0) == int(ds[0].num_nodes('Personen') * 0.1)



@unittest.skipIf(F._default_context_str == 'gpu', reason="Datasets don't need to be tested on GPU.")
def test_as_linkpred():
    # create
    ds = data.AsLinkPredDataset(data.CoraGraphDataset(), split_ratio=[0.8, 0.1, 0.1], neg_ratio=1, verbose=True)
    # Cora has 10556 edges, 10% test edges can be 1057
    assert ds.test_edges[0][0].shape[0] == 1057
    # negative samples, not guaranteed, so the assert is in a relaxed range
    assert 1000 <= ds.test_edges[1][0].shape[0] <= 1057
    # read from cache
    ds = data.AsLinkPredDataset(data.CoraGraphDataset(), split_ratio=[0.7, 0.1, 0.2], neg_ratio=2, verbose=True)
    assert ds.test_edges[0][0].shape[0] == 2112
    # negative samples, not guaranteed to be ratio 2, so the assert is in a relaxed range
    assert 4000 < ds.test_edges[1][0].shape[0] <= 4224


@unittest.skipIf(dgl.backend.backend_name != 'pytorch', reason="ogb only supports pytorch")
def test_as_linkpred_ogb():
    from ogb.linkproppred import DglLinkPropPredDataset
    ds = data.AsLinkPredDataset(DglLinkPropPredDataset("ogbl-collab"), split_ratio=None, verbose=True)
    # original dataset has 46329 test edges
    assert ds.test_edges[0][0].shape[0] == 46329
    # force generate new split
    ds = data.AsLinkPredDataset(DglLinkPropPredDataset("ogbl-collab"), split_ratio=[0.7, 0.2, 0.1], verbose=True)
    assert ds.test_edges[0][0].shape[0] == 235812

@unittest.skipIf(F._default_context_str == 'gpu', reason="Datasets don't need to be tested on GPU.")
def test_as_nodepred_csvdataset():
    with tempfile.TemporaryDirectory() as test_dir:
        # generate YAML/CSVs
        meta_yaml_path = os.path.join(test_dir, "meta.yaml")
        edges_csv_path = os.path.join(test_dir, "test_edges.csv")
        nodes_csv_path = os.path.join(test_dir, "test_nodes.csv")
        meta_yaml_data = {'version': '1.0.0', 'dataset_name': 'default_name',
                          'node_data': [{'file_name': os.path.basename(nodes_csv_path)
                                         }],
                          'edge_data': [{'file_name': os.path.basename(edges_csv_path)
                                         }],
                          }
        with open(meta_yaml_path, 'w') as f:
            yaml.dump(meta_yaml_data, f, sort_keys=False)
        num_nodes = 100
        num_edges = 500
        num_dims = 3
        num_classes = num_nodes
        feat_ndata = np.random.rand(num_nodes, num_dims)
        label_ndata = np.arange(num_classes)
        df = pd.DataFrame({'node_id': np.arange(num_nodes),
                           'label': label_ndata,
                           'feat': [line.tolist() for line in feat_ndata],
                           })
        df.to_csv(nodes_csv_path, index=False)
        df = pd.DataFrame({'src_id': np.random.randint(num_nodes, size=num_edges),
                           'dst_id': np.random.randint(num_nodes, size=num_edges),
                           })
        df.to_csv(edges_csv_path, index=False)

        ds = data.DGLCSVDataset(test_dir, force_reload=True)
        assert 'feat' in ds[0].ndata
        assert 'label' in ds[0].ndata
        assert 'train_mask' not in ds[0].ndata
        assert not hasattr(ds[0], 'num_classes')
        new_ds = data.AsNodePredDataset(ds, split_ratio=[0.8, 0.1, 0.1], force_reload=True)
        assert new_ds.num_classes == num_classes
        assert 'feat' in new_ds[0].ndata
        assert 'label' in new_ds[0].ndata
        assert 'train_mask' in new_ds[0].ndata

if __name__ == '__main__':
    test_minigc()
    test_gin()
    test_data_hash()
    test_tudataset_regression()
    test_fraud()
    test_fakenews()
    test_extract_archive()
    test_csvdataset()
    test_add_nodepred_split()
    test_as_nodepred1()
    test_as_nodepred2()
    test_as_nodepred_csvdataset()
