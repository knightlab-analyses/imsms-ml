def list_genera(df, woltka_meta_df, min_sample_count=0, min_genus_count=0):
    woltka_included = woltka_meta_df[woltka_meta_df['#genome'].isin(df.columns)]
    vcs = woltka_included['genus'].value_counts()
    genera = sorted(vcs[vcs>1].index.astype(str).tolist())

    filt_genera = ['all']
    for g in genera:
        filtered_df = df[list_woltka_refs(df, woltka_meta_df, g)['#genome']]
        filtered_df_sum = filtered_df.sum(axis=1)
        filtered_df = filtered_df[filtered_df_sum >= min_genus_count]
        if len(filtered_df) >= min_sample_count:
            filt_genera.append(g)
    return filt_genera


def list_woltka_refs(df, woltka_meta_df, genus=None):
    woltka_included = woltka_meta_df[woltka_meta_df['#genome'].isin(df.columns)]

    if genus is None:
        refs = woltka_included
    else:
        refs = woltka_included[woltka_included['genus']==genus]

    filtered_df = df[refs['#genome']]
    col_sums = filtered_df.sum()
    col_sums.name='total'
    refs = refs.join(col_sums, on='#genome')

    refs = refs.reset_index()
    refs = refs.sort_values(["total", "#genome"], ascending=False)[['total', '#genome','species']]
    return refs


def filter_and_sort_df(df, woltka_meta_df, genus, min_genus_count=0):
    if genus == 'all':
        refs_df = list_woltka_refs(df, woltka_meta_df)
    else:
        refs_df = list_woltka_refs(df, woltka_meta_df, genus)

    genomes = refs_df['#genome'].tolist()
    filtered_df = df[genomes]

    filtered_df_sum = filtered_df.sum(axis=1)
    filtered_df = filtered_df[filtered_df_sum >= min_genus_count]
    return filtered_df