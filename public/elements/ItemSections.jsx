export default function ItemSections() {
  const {
    sections = [],     // [{ title, items: [{name,url}] }]
    size = 28,         // icon size (px)
    cols = 4,          // columns
    dense = true       // spacing
  } = props;

  if (!sections.length) return null;

  const wrap = (s) => s?.toString().trim() || "";

  // vertical & horizontal padding per chip
  const pY = dense ? 6 : 8;
  const pX = dense ? 8 : 10;

  // FIXED chip height: icon + vertical padding
  const rowH = size + pY * 2;

  const page = {
    display: "flex",
    flexDirection: "column",
    gap: dense ? 12 : 16
  };

  const sectionBox = {
    display: "grid",
    gridTemplateColumns: `repeat(${cols}, 1fr)`,
    gap: dense ? 8 : 12,
    alignItems: "stretch",
    // 👇 Force every row to the same height
    gridAutoRows: `${rowH}px`
  };

  const chip = {
    display: "flex",
    alignItems: "center",
    gap: 8,
    padding: `${pY}px ${pX}px`,
    borderRadius: 12,
    background: "rgba(0,0,0,0.35)",
    color: "inherit",
    backdropFilter: "blur(4px)",
    WebkitBackdropFilter: "blur(4px)",
    // 👇 Fill the entire grid cell so all chips are equal size
    width: "100%",
    height: "100%",
    boxSizing: "border-box",
    minWidth: 0
  };

  const imgStyle = {
    width: size,
    height: size,
    objectFit: "cover",
    borderRadius: 6,
    flex: "0 0 auto"
  };

  // 👇 Single-line, ellipsized names to keep uniform height
  const nameStyle = {
    overflow: "hidden",
    whiteSpace: "nowrap",
    textOverflow: "ellipsis"
  };

  const titleStyle = {
    fontWeight: 600,
    opacity: 0.9,
    marginBottom: 6
  };

  return (
    <div style={page}>
      {sections.map((sec, i) => (
        <div key={i}>
          <div style={titleStyle}>{wrap(sec.title)}</div>
          <div style={sectionBox}>
            {(sec.items || []).map((it, j) => (
              <div key={j} style={chip} title={wrap(it.name)}>
                <img
                  src={wrap(it.url)}
                  alt={wrap(it.name)}
                  width={size}
                  height={size}
                  loading="lazy"
                  decoding="async"
                  style={imgStyle}
                  onError={(e) => { e.currentTarget.style.visibility = "hidden"; }}
                />
                <span style={nameStyle}>{wrap(it.name)}</span>
              </div>
            ))}
          </div>
        </div>
      ))}
    </div>
  );
}
