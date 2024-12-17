var num1 = Math.floor(Math.random() * 10);
var num2 = Math.floor(Math.random() * 10);
var num3 = Math.floor(Math.random() * 10);
var num4 = Math.floor(Math.random() * 10);
var num5 = Math.floor(Math.random() * 10);
var num6 = Math.floor(Math.random() * 10);
var num7 = Math.floor(Math.random() * 10);


var ynum1;
var ynum2;
var ynum3;
var ynum4;
var ynum5;
var ynum6;
var ynum7;

function loto() {

    ynum1 = document.getElementById("ynum1").value;
    ynum2 = document.getElementById("ynum2").value;
    ynum3 = document.getElementById("ynum3").value;
    ynum4 = document.getElementById("ynum4").value;
    ynum5 = document.getElementById("ynum5").value;
    ynum6 = document.getElementById("ynum6").value;
    ynum7 = document.getElementById("ynum7").value;

    document.getElementById("snum1").innerHTML = ynum1 + " - ";
    document.getElementById("snum2").innerHTML = ynum2 + " - ";
    document.getElementById("snum3").innerHTML = ynum3 + " - ";
    document.getElementById("snum4").innerHTML = ynum4 + " - ";
    document.getElementById("snum5").innerHTML = ynum5 + " - ";
    document.getElementById("snum6").innerHTML = ynum6 + " - ";
    document.getElementById("snum7").innerHTML = ynum7;

    setTimeout(function(){document.getElementById("num1").innerHTML = num1}, 9000); 
    setTimeout(function(){document.getElementById("num2").innerHTML = num2}, 9250); 
    setTimeout(function(){document.getElementById("num3").innerHTML = num3}, 9500); 
    setTimeout(function(){document.getElementById("num4").innerHTML = num4}, 9750); 
    setTimeout(function(){document.getElementById("num5").innerHTML = num5}, 10000); 
    setTimeout(function(){document.getElementById("num6").innerHTML = num6}, 10250); 
    setTimeout(function(){document.getElementById("num7").innerHTML = num7}, 10500); 

    var timeleft = 9;
    var downloadTimer = setInterval(function(){
    timeleft--;
    document.getElementById("countdowntimer").textContent = "End to Change Your Mind " + timeleft;
    if(timeleft <= 0)
        clearInterval(downloadTimer);
    },1000);

    num1 = "1";

    setTimeout(function(){
        if(ynum1 == num1){
            ynum1 = true;
        }else{
            ynum1 = false;
        }
        if(ynum2 == num2){
            ynum2 = true;
        }else{
            ynum2 = false;
        }
        if(ynum3 == num3){
            ynum3 = true;
        }else{
            ynum3 = false;
        }
        if(ynum4 == num4){
            ynum4 = true;
        }else{
            ynum4 = false;
        }
        if(ynum5 == num5){
            ynum5 = true;
        }else{
            ynum5 = false;
        }
        if(ynum6 == num6){
            ynum6 = true;
        }else{
            ynum6 = false;
        }
        if(ynum7 == num7){
            ynum7 = true;
        }else{
            ynum7 = false;
        }
        
        var say = new Array(ynum1,ynum2,ynum3,ynum4,ynum5,ynum6,ynum7);
        var count = say.filter(Boolean).length;

        if(count == "1"){
            document.getElementById("last").innerHTML = count + " - Congratulations You Won Amortized By Knowing The Correct Number!"
        }else if(count == "2"){
            document.getElementById("last").innerHTML = count + " - Congratulations You Won 500 $ By Knowing The Correct Number!"
        }else if(count == "3"){
            document.getElementById("last").innerHTML = count + " - Congratulations You Won 5.000 $ By Knowing The Correct Number!"
        }else if(count == "4"){
            document.getElementById("last").innerHTML = count + " - Congratulations You Won 10.000 $ By Knowing The Correct Number!"
        }else if(count == "5"){
            document.getElementById("last").innerHTML = count + " - Congratulations You Won 200.000 $ By Knowing The Correct Number!"
        }else if(count == "6"){
            document.getElementById("last").innerHTML = count + " - Congratulations You Won 500.000 $ By Knowing The Correct Number!"
        }else if(count == "7"){
            document.getElementById("last").innerHTML = count + " - Congratulations You Won 1.000.000 $ By Knowing The Correct Number!"
        }else{
            document.getElementById("last").innerHTML = count + " - You Didn't Know Any Number Don't Worry, Hope to See You Next Time!"
        }
        
    }, 11000); 
    
}
