import {loadFont as telugu} from '@remotion/google-fonts/NotoSansTelugu';
import {loadFont as ramabhadra} from '@remotion/google-fonts/Ramabhadra';
import {loadFont as devanagari} from '@remotion/google-fonts/NotoSansDevanagari';
import {loadFont as latin} from '@remotion/google-fonts/NotoSans';

export const TE = telugu('normal', {weights: ['500', '700', '800'], subsets: ['telugu', 'latin']}).fontFamily + ", 'Nirmala UI'";
export const TITLE = ramabhadra('normal', {subsets: ['telugu', 'latin']}).fontFamily + ', ' + TE;
export const DEV = devanagari('normal', {weights: ['500', '700'], subsets: ['devanagari', 'latin']}).fontFamily + ", 'Nirmala UI'";
latin('italic', {weights: ['400'], subsets: ['latin', 'latin-ext']});
export const LAT = latin('normal', {weights: ['500', '700'], subsets: ['latin', 'latin-ext']}).fontFamily + ", 'Segoe UI'";
