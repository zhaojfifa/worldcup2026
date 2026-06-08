interface Props {
  em: string;
  title: string;
  body: string;
  okLabel: string;
  onOk: () => void;
  onClose: () => void;
}

export function Modal({ em, title, body, okLabel, onOk, onClose }: Props) {
  return (
    <div className="overlay" onClick={onClose}>
      <div className="modal" onClick={e => e.stopPropagation()}>
        <div className="em">{em}</div>
        <div className="h">{title}</div>
        <div className="p">{body}</div>
        <button className="cta primary" style={{ marginTop: 18 }} onClick={() => { onClose(); onOk(); }}>
          {okLabel}
        </button>
      </div>
    </div>
  );
}
