// Minimal declaration for the 'qrcode' package (admin-only QR preview).
// Full @types/qrcode pulls in @types/node, which breaks browser-only typings.
declare module 'qrcode' {
  export function toDataURL(text: string, opts?: { width?: number; margin?: number }): Promise<string>;
  const QRCode: { toDataURL: typeof toDataURL };
  export default QRCode;
}
