export function isValidPrice(price: string): boolean {
  return price === '' || /^[0-9]*(\.[0-9]{0,2})?$/.test(price);
}