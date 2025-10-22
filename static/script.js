function toggleLike(reviewId) {
  const likeBtn = document.getElementById("like-btn");
  fetch(`/like/${reviewId}`, { method: "POST" })
    .then((response) => response.json())
    .then((data) => {
      document.getElementById("like-count").innerText = data.like_count;
      if (data.liked) {
        likeBtn.setAttribute("data-liked", "true");
        likeBtn.classList.add("liked");
      } else {
        likeBtn.setAttribute("data-liked", "false");
        likeBtn.classList.remove("liked");
      }
    });
}
document.querySelectorAll('.like-form').forEach(form => {
    form.addEventListener('submit', function(e){
        e.preventDefault();
        const reviewId = this.dataset.reviewId;
        fetch(`/like/${reviewId}`, { method: 'POST' })
        .then(res => res.json())
        .then(data => {
            const btn = this.querySelector('.like-btn');
            const span = document.getElementById(`like-count-${reviewId}`);
            span.textContent = `${data.like_count} Likes`;
            if(data.liked){
                btn.classList.add('liked');
            } else {
                btn.classList.remove('liked');
            }
        });
    });
});
