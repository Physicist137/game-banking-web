// This code is by far definitely not ready at all.
// This code has to correctly deal with minuses, pluses, etc
// Perhaps even change background color from blue to red if negative.

var signal = 1;

function correct_money(value_string, exponent) {
	let last = value_string[value_string.length - 1]
	let str = value_string.replace(/,/g, '');

	let num = parseFloat(str);
	if (value_string == "") num = 0.0;
	else if (last == "-"  &&  num >= 0) num *= -1;
	else if (last == "+"  &&  num <= 0) num *= -1;
	else if (value_string.length == 1) num = parseFloat(str) * (10 ** (-exponent))
	else num = 10*parseFloat(str);

	/*console.log("value_string:" + value_string)
	console.log("last: " + last)
	console.log(num)*/

	return num.toFixed(exponent).replace(/(\d)(?=(\d{3})+(?!\d))/g, '$1,');
}
