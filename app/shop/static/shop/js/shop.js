export const addToCart = (code, title, price) => {
  document.getElementById('product-code').value = code
  document.getElementById('product-title').innerText = title
  document.getElementById('product-price').innerText = '$' + price
}
