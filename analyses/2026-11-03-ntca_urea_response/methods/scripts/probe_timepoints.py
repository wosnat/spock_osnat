import sys; sys.path.insert(0, "analyses/2026-11-03-ntca_urea_response/methods")
import ntca_urea as m
for e in ["10.1038/msb4100087_nitrogen_nitrogen_deprivation_med4_med4_microarray",
          "10.1038/msb4100087_nitrogen_nitrogen_deprivation_mit9313_mit9313_microarray"]:
    df = m.fetch_de([e])
    print(e, len(df), df.groupby(["timepoint_order", "timepoint"]).size().to_dict())
