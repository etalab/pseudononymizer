var form = document.getElementById('text-form');


form.addEventListener("submit", print_results);

function nl2br (str, is_xhtml) {
  // http://kevin.vanzonneveld.net
  // +   original by: Kevin van Zonneveld (http://kevin.vanzonneveld.net)
  // +   improved by: Philip Peterson
  // +   improved by: Onno Marsman
  // +   improved by: Atli Þór
  // +   bugfixed by: Onno Marsman
  // +      input by: Brett Zamir (http://brett-zamir.me)
  // +   bugfixed by: Kevin van Zonneveld (http://kevin.vanzonneveld.net)
  // +   improved by: Brett Zamir (http://brett-zamir.me)
  // +   improved by: Maximusya
  // *     example 1: nl2br('Kevin\nvan\nZonneveld');
  // *     returns 1: 'Kevin<br />\nvan<br />\nZonneveld'
  // *     example 2: nl2br("\nOne\nTwo\n\nThree\n", false);
  // *     returns 2: '<br>\nOne<br>\nTwo<br>\n<br>\nThree<br>\n'
  // *     example 3: nl2br("\nOne\nTwo\n\nThree\n", true);
  // *     returns 3: '<br />\nOne<br />\nTwo<br />\n<br />\nThree<br />\n'
  var breakTag = (is_xhtml || typeof is_xhtml === 'undefined') ? '<br ' + '/>' : '<br>'; // Adjust comment to avoid issue on phpjs.org display

  return (str + '').replace(/([^>\r\n]?)(\r\n|\n\r|\r|\n)/g, '$1' + breakTag + '$2');
}

function try2(url_API, text, tags=false){
    var data = new FormData();
    data.append( "text", text);
    // if (tags != false)
    // {
    //     data.append("tags", tags);
    // }
    fetch(url_API,
    {
        method: "POST",
        body: data
    })
    .then(function(res){ return res.json(); })
    .then(function(data){
        var div_pseudonym = document.getElementById('pseudonymized_txt');
        var div_tagged = document.getElementById('tagged_txt');
        div_tagged.title = "SUPER TAGGED!"  
        div_pseudonym.innerHTML = "<h3> " + "PSEUDONYMIZED TEXT" + "</h3>";
        div_pseudonym.innerHTML += "<p> " + nl2br(data.pseudonim_text);
        
        div_tagged.innerHTML = "<h3> " + "TAGGED TEXT" + "</h3>";
        div_tagged.innerHTML += "<p> " + nl2br(data.tagged_text);
        // alert( JSON.stringify( data ) ) 
        })
}



function print_results(event) {
  event.preventDefault();
  // document.getElementById("present_result").innerHTML = "";
  if(this.elements.query.value === '') {
    alert("Enter search word!");
  } else {

    const text =  this.elements.query.value;
    

    // var http = new XMLHttpRequest();
    var url = 'http://localhost:5001/tag';

    try2(url, text)

  }
}

