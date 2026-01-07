import polars as pl
from pathlib import Path

def main():
	data_path = Path("../data")
	map_path = Path("../map")

	pad_xy = pl.read_csv(data_path / "padxy.csv")
	pad_scale = pl.read_csv(data_path / "padscale.csv")
	pad_updown = pl.read_csv(data_path / "padupdown.csv")
	rcnp_map = pl.read_csv(data_path / "rcnp_map.csv")
	pad_map = (
		rcnp_map
		.filter(pl.col("det keyword") == "pad")
		.select(["cobo", "asad", "aget", "aget channel", "det channel"])
	)

	pad_xy = pad_xy.with_row_index("pad")
	pad_scale = pad_scale.with_row_index("pad")
	pad_updown = pad_updown.with_row_index("pad")
	pad_map = pad_map.rename({
		"aget channel": "channel",
		"det channel": "pad"
	})

	joined = (
		pad_xy
		.join(pad_scale, on="pad", how="left")
		.join(pad_updown, on="pad", how="left")
		.join(pad_map, on="pad", how="left")
	)

	edge = 4.908235
	offset = edge * (3**0.5) / 6
	joined = joined.with_columns(
		pl.col("x").alias("cx"),
		(
			pl.when(pl.col("direction") == 0)
			.then(pl.col("y") - offset*pl.col("scale"))
			.otherwise(pl.col("y") + offset*pl.col("scale"))
			.alias("cy")
		)
	)

	joined.write_json(map_path / "pads.json")
	joined.write_csv(data_path / "pads.csv")

if __name__ == "__main__":
	main()