import { useEffect, useState, useCallback } from 'react';

let _show: (msg: string) => void = () => {};

export function toast(msg: string) { _show(msg); }

export function ToastProvider() {
  const [msg, setMsg] = useState('');
  const [visible, setVisible] = useState(false);
  const timerRef = { current: 0 as ReturnType<typeof setTimeout> };

  const show = useCallback((m: string) => {
    setMsg(m);
    setVisible(true);
    clearTimeout(timerRef.current);
    timerRef.current = setTimeout(() => setVisible(false), 1800);
  }, []);

  useEffect(() => { _show = show; }, [show]);

  if (!visible) return null;
  return <div className="toast-wrap">{msg}</div>;
}
