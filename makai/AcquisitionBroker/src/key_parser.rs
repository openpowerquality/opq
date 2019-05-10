use regex::Regex;

pub fn parse_key_file(key_file_contents :&String) -> (Option<String>, Option<String>){

    let mut pub_key = None;
    let mut sec_key = None;

    let p_re = Regex::new(r#"public-key\s+=\s+"(.+)""#).unwrap();
    let s_re = Regex::new(r#"secret-key\s+=\s+"(.+)""#).unwrap();

    for caps in p_re.captures_iter(&key_file_contents) {
        pub_key = Some(caps.get(1).unwrap().as_str().to_string());
        break;
    }

    for caps in s_re.captures_iter(&key_file_contents) {
        sec_key = Some(caps.get(1).unwrap().as_str().to_string());
        break;
    }


    (pub_key,sec_key)
}