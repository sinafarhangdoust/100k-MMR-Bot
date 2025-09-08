export default function ItemSections() {
  const {
    sections = [],    // [{ title: "Start", items: [{name,url}, ...] }, ...]
    size = 28,        // icon size in px
    cols = 4,         // items per row (responsive enough for chat width)
    dense = true      // tighter spacing
  } = props;

  const wrap = (s) => s?.trim() || "";

  const page = {
    display: "flex",
    flexDirection: "column",
    gap: dense ? 12 : 16
  };

  const sectionBox = {
    display: "grid",
    gridTemplateColumns: `repeat(${cols}, minmax(0, 1fr))`,
    gap: dense ? 8 : 12,
    alignItems: "start"
  };

  const chip = {
    display: "flex",
    alignItems: "center",
    gap: 8,
    padding: dense ? "6px 8px" : "8px 10px",
    borderRadius: 12,
    background: "rgba(0,0,0,0.35)",
    color: "inherit",
    backdropFilter: "blur(4px)",
    WebkitBackdropFilter: "blur(4px)",
    minWidth: 0  // allow text wrapping
  };

  const imgStyle = {
    width: size,
    height: size,
    objectFit: "cover",
    borderRadius: 6,
    flex: "0 0 auto"
  };

  const titleStyle = {
    fontWeight: 600,
    opacity: 0.9,
    marginBottom: 6
  };

  if (!sections.length) return null;

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
                <span style={{wordBreak: "break-word"}}>{wrap(it.name)}</span>
              </div>
            ))}
          </div>
        </div>
      ))}
    </div>
  );
}