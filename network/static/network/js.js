document.addEventListener('DOMContentLoaded', function() {
      document.querySelectorAll('.btn').forEach(function(button){
      button.addEventListener('click', edit_post);
      })

      document.querySelectorAll('.bi-heart').forEach(function(i){
        i.addEventListener('click', like_post);
        })

      document.querySelectorAll('.bi-heart-fill').forEach(function(i){
        i.addEventListener('click', like_post);
        })

  });

  function edit_post() {
    let dv = this.parentElement;
    let cont = dv.querySelector('.content')
    if (this.innerHTML == 'Edit') {
      this.innerHTML = 'Save';
      cont.style.display = 'none'
      let tx = document.createElement('textarea');
      tx.style.textAlign = 'left';
      tx.style.width = '90vw';
      tx.setAttribute('id', 'edit');
      tx.innerHTML = dv.querySelector('.cont').innerHTML;
      const b = document.createElement('br')
      let d = document.createElement('div')
      d.appendChild(b);
      d.appendChild(tx);
      dv.appendChild(d);
      dv.style.caretColor = "auto";
    } else {
      this.innerHTML = 'Edit';
      const edpost = dv.querySelector('#edit').value;
      const ids = dv.querySelector('.postid').innerHTML;
      const id = parseInt(ids);
      dv.querySelector('.cont').innerHTML = edpost;
      const ce = dv.lastElementChild;
      dv.removeChild(ce);
      cont.style.display = 'block';
      fetch(`/edit/${id}`, {
        method: 'PUT',
        headers: {"X-CSRFToken": getCookie('csrftoken'),},           
        body: JSON.stringify({
           'edpost': edpost
        })
      })
      dv.style.caretColor = "transparent";
    }
  }


  function like_post() {
    let dv = this.parentElement;
    const ids = dv.querySelector('.postid').innerHTML;
    const id = parseInt(ids);  
    let val = parseInt(this.innerHTML);
    if (this.classList.contains('bi-heart-fill')) {
      let empty = dv.querySelector('.bi-heart');
      empty.style.display = 'block';
      this.style.display = 'none';
      empty.innerHTML=val-1;
//      like = false
    } else {
      let filled = dv.querySelector('.bi-heart-fill');
      filled.style.display = 'block';
      this.style.display = 'none';
      filled.innerHTML=val+1;
//      like = true
    }
    fetch(`/like/${id}`, {
      method: 'PUT',
      headers: {"X-CSRFToken": getCookie('csrftoken'),},
//      body: JSON.stringify({
//        'like': like
//      })          
    })
  }
  
  
  function getCookie(cname) {
    let name = cname + "=";
    let decodedCookie = decodeURIComponent(document.cookie);
    let ca = decodedCookie.split(';');
    for(let i = 0; i <ca.length; i++) {
      let c = ca[i];
      while (c.charAt(0) == ' ') {
        c = c.substring(1);
      }
      if (c.indexOf(name) == 0) {
        return c.substring(name.length, c.length);
      }
    }
    return "";
  }
