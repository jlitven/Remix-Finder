 $(document).ready(function(e) {
    // Change active menu on click
    $("#font-menu a").on("click", function(){
       $("#font-menu").find(".active").removeClass("active");
       $(this).parent().addClass("active");
       var font_family = $(this).html();
       UpdateFont(font_family);
       return false;
    });

    $("#name-menu a").on("click", function(){
       $("#name-menu").find(".active").removeClass("active");
       $(this).parent().addClass("active");
       var flag = $(this).html();
       UpdateName(flag);
       return false;
    });

 });

 function UpdateFont(font_family){
    // TODO: Fix Hack
     var elements = document.getElementsByClassName("quote");
     var i;
     for (i= 0; i < elements.length;i++){
         elements[i].style.fontFamily = font_family;
     }
     var elements = document.getElementsByClassName("author_name");
     for (i= 0; i < elements.length;i++){
         elements[i].style.fontFamily = font_family;
     }
 }

 function UpdateName(flag){
    var elements = document.getElementsByClassName("author_name");
    var i;
    for (i = 0; i < elements.length;i++){
        if (flag == "No"){
            elements[i].style.display = 'none';
        }else{
            elements[i].style.display = 'inherit';
        }
    }
 }

 function CurrentFontFamily(){
  var menu = document.getElementById("font-menu");
  var font_family = menu.getElementsByClassName("active")[0].getElementsByTagName("a")[0].innerHTML;
  return font_family;
 }


function CreatePDF(author_name){
    var quote_area = document.getElementById(author_name + " quote_area");
    var text = quote_area.innerHTML;
    var font_family = CurrentFontFamily();
    pdf_url = Flask.url_for("single_pdf", {"author": author_name, "quote": text, "font_family": font_family});
    window.open(pdf_url, '_blank');
    return false;
}

function next(author_name){
    var quote_area = document.getElementById(author_name + " quote_area");
    var quote_id = quote_area.getAttribute("data_quote_id");
    var next_id = parseInt(quote_id) + 1;
    var next_quote = document.getElementById(author_name + " quote_" + next_id);
    if (next_quote != null) {
        var text = next_quote.getAttribute("data");
        quote_area.innerHTML = text;
        quote_area.setAttribute("data_quote_id", next_id);
    }

}

function previous(author_name){
    var quote_area = document.getElementById(author_name + " quote_area");
    var quote_id = quote_area.getAttribute("data_quote_id");
    var prev_id = parseInt(quote_id) - 1;
    var prev_quote = document.getElementById(author_name + " quote_" + prev_id);

    if (prev_quote != null){
        var text = prev_quote.getAttribute("data");
        quote_area.innerHTML = text;
        quote_area.setAttribute("data_quote_id", prev_id);
    }
}
