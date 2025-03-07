.. _api-dataloading:

dgl.dataloading
=================================

.. automodule:: dgl.dataloading

DataLoaders
-----------
.. currentmodule:: dgl.dataloading.pytorch

DGL DataLoader for mini-batch training works similarly to PyTorch's DataLoader.
It has a generator interface that returns mini-batches sampled from some given graphs.
DGL provides two DataLoaders: a ``NodeDataLoader`` for node classification task
and an ``EdgeDataLoader`` for edge/link prediction task.

.. autoclass:: NodeDataLoader
.. autoclass:: EdgeDataLoader
.. autoclass:: GraphDataLoader
.. autoclass:: DistNodeDataLoader
.. autoclass:: DistEdgeDataLoader

.. _api-dataloading-neighbor-sampling:

Neighbor Sampler
----------------
.. currentmodule:: dgl.dataloading.neighbor

Neighbor samplers are classes that control the behavior of ``DataLoader`` s
to sample neighbors. All of them inherit the base :class:`BlockSampler` class, but implement
different neighbor sampling strategies by overriding the ``sample_frontier`` or
the ``sample_blocks`` methods.

.. autoclass:: BlockSampler
    :members: sample_frontier, sample_blocks, sample

.. autoclass:: MultiLayerNeighborSampler
    :members: sample_frontier
    :show-inheritance:

.. autoclass:: MultiLayerFullNeighborSampler
    :show-inheritance:

Subgraph Iterators
------------------
Subgraph iterators iterate over the original graph in subgraphs. One should use subgraph
iterators with ``GraphDataLoader`` like follows:

.. code:: python

   sgiter = dgl.dataloading.ClusterGCNSubgraphIterator(
       g, num_partitions=100, cache_directory='.', refresh=True)
   dataloader = dgl.dataloading.GraphDataLoader(sgiter, batch_size=4, num_workers=0)
   for subgraph_batch in dataloader:
       train_on(subgraph_batch)

.. autoclass:: dgl.dataloading.dataloader.SubgraphIterator

.. autoclass:: dgl.dataloading.cluster_gcn.ClusterGCNSubgraphIterator

ShaDow-GNN Subgraph Sampler
---------------------------
.. currentmodule:: dgl.dataloading.shadow

.. autoclass:: ShaDowKHopSampler

.. _api-dataloading-collators:

Collators
---------
.. currentmodule:: dgl.dataloading

Collators are platform-agnostic classes that generates the mini-batches
given the graphs and indices to sample from.

.. autoclass:: NodeCollator
.. autoclass:: EdgeCollator
.. autoclass:: GraphCollator

.. _api-dataloading-negative-sampling:

Negative Samplers for Link Prediction
-------------------------------------
.. currentmodule:: dgl.dataloading.negative_sampler

Negative samplers are classes that control the behavior of the ``EdgeDataLoader``
to generate negative edges.

.. autoclass:: Uniform
    :members: __call__

.. autoclass:: GlobalUniform
    :members: __call__

Async Copying to/from GPUs
--------------------------
.. currentmodule:: dgl.dataloading

Data can be copied from the CPU to the GPU
while the GPU is being used for
computation, using the :class:`AsyncTransferer`.
For the transfer to be fully asynchronous, the context the
:class:`AsyncTranserer`
is created with must be a GPU context, and the input tensor must be in 
pinned memory.


.. autoclass:: AsyncTransferer
    :members: __init__, async_copy

.. autoclass:: async_transferer.Transfer
    :members: wait
