#encoding "utf-8"

Person -> Word<kwtype="персоны">;
Attraction -> Word<kwtype="достопримечательности">;
Contains -> Person interp (Contains.Person);
Contains -> Attraction interp (Contains.Attraction);
