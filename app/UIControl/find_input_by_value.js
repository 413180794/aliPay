function find_input_by_value(input_list,value){
    for(var i = 0;i<input_list.length;i++){
        if (input_list[i].value = value ){
            return input_list[i];
        }
    }
    return null;
}