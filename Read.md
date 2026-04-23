Stopword nedir?                                                                
                                                                               
  Bir dilde çok sık geçen ama kendi başına anlam taşımayan kelimeler — "ve",     
  "bir", "bu", "ile", "için" gibi.                                               
                                                                                 
  Bu pipeline'da ne için kullanıyoruz?                                           
                                                                                 
  Burada kalite filtresi olarak kullanıyoruz. Mantığı şu:                        
                                                            
  ▎ Eğer bir belge Türkçeyse, içinde kaçınılmaz olarak Türkçe stopword'ler       
  ▎ geçmesi lazım.                                          
                                                                                 
  "Merhaba bu bir test cümlesidir ve çok güzel."            
             ^^^     ^^^          ^^^                                            
          stopword stopword    stopword  → oran yüksek → KALITELI                
                                                                                 
  "asdfgh zxcvbn qwerty 12345 @@@ http://spam.com"                               
      → hiç stopword yok → oran 0 → ATILIR                                       
                                                                                 
  Yani stopword oranı düşük olan belgeler şunlar oluyor:                         
  - Spam / reklam metinleri                                                      
  - Sadece URL listesi olan sayfalar                                             
  - Kod/sembol çorbası                                      
  - Yabancı dilde yazılmış metinler (Türkçe stopword geçmez)                     
                                                                                 
  Parametredeki karşılığı                                                        
                                                                                 
  parameters.py'de şöyle bir şey olacak:                                         
  "stopwords_min_cutoff": 0.10  # belgenin en az %10'u stopword olmalı           
                                                                                 
  Altında kalan belgeler atılır.                                                 
   


NOT2:

parameters.py'da yaptıklarını tam anlamadım , mesela diyelim ki bir cümlede    
  çok uzun bir kelime var sadece kelimeyi atarsak cümle anlamsız olmaz mı, tüm   
  cümle mi atılıyor?                                                             
                                                                                 
⏺ Çok iyi soru. Şu an tüm belge (document) seviyesinde çalışıyoruz, cümle değil. 
                                                                                
  Pipeline'ın mantığı şöyle:                                                     
   
  VERİ SETİ                                                                      
  └── Belge 1: "Türkiye'nin başkenti Ankara'dır. ..."   ← tüm bu metin bir birim 
  └── Belge 2: "asdfgh http://spam.com @@@@@@@@@@"      ← tüm bu metin bir birim 
                                                                                 
  └── Belge 3: "buy cheap viagra xxxxxxxxxxxxxxxxxxx"   ← tüm bu metin bir birim 
                                                                                 
  Her filtre bir belgeye bakıp "bu belgeyi tut mu, at mı?" kararı veriyor.       
                                                            
  ---                                                                            
  length_word_max_cutoff özelinde:                          
                                                                                 
  "cond_remove_long_words": True,
  "length_word_max_cutoff": 40,                                                  
                                                                                 
  Bu şu demek: belgede 40 karakterden uzun bir kelime varsa belgenin tamamı      
  atılır.                                                                        
                                                                                 
  Neden? Çünkü gerçek Türkçe metinlerde bile 40+ karakterlik kelime neredeyse    
  yok. Eğer varsa büyük ihtimalle:
  - asdfjklasdfjklasdfj — rastgele karakter dizisi                               
  - http://cokuzunbirdomain.com/path/to/page — URL parçası                       
  - AAAAAAAAAAAAAAAAAAAAAAAAA — tekrar karakterler        
                                                                                 
  Yani bu filtre kelimeyi değil, o kirli belgeyi atmak için var.                 
                                                                                 
  ---                                                                            
  Genel tablo:                                                                   
                                                                                 
  ┌──────────────────────────┬────────────────────────────────────────────────┐
  │          Filtre          │                   Ne atılır                    │  
  ├──────────────────────────┼────────────────────────────────────────────────┤
  │ length_word_max_cutoff   │ İçinde aşırı uzun kelime olan belge            │
  ├──────────────────────────┼────────────────────────────────────────────────┤
  │ number_words_min_cutoff  │ 15'ten az kelimeli belge (başlık listesi,      │  
  │                          │ stub)                                          │  
  ├──────────────────────────┼────────────────────────────────────────────────┤  
  │ character_repetition     │ aaaaaaa oranı yüksek belge                     │  
  ├──────────────────────────┼────────────────────────────────────────────────┤
  │ stopwords_min_cutoff     │ Türkçe stopword oranı düşük belge              │  
  ├──────────────────────────┼────────────────────────────────────────────────┤
  │ flagged_words_max_cutoff │ Uygunsuz kelime oranı yüksek belge             │  
  └──────────────────────────┴────────────────────────────────────────────────┘
                                                                                 
  Hepsi belge seviyesinde karar veriyor. Kelime veya cümle bazında hiçbir şey    
  kesmiyoruz — ya tüm belge kalıyor ya da tüm belge gidiyor.
                                                             