All Preprocessing steps take a PipelineState and produce a PipelineState.
That means that they can be configured and chained together by the researcher.

Preprocessing steps are simple operations like
    * Filtering rows by some function of their index
    * Mapping the index label to some other index label
    * Identifying groups of rows with the same index label and merging them in
        some way
