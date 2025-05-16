import os
import csv
import json

CURRENT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PARENT_DIR = os.path.dirname(CURRENT_DIR)
EVALUATOR_DIR = os.path.join(CURRENT_DIR, "config_files")
TRAJECTORY_DIR = os.path.join(PARENT_DIR, "AgentOccam-Trajectories")
OUTPUT_DIR = os.path.join(CURRENT_DIR, "output")
HOMEPAGE_URL = "localhost:4399"


TASK_ID_DICT = {
    "ALL": list(range(812)),
    "SHOPPING_ADMIN": [0, 1, 2, 3, 4, 5, 6, 11, 12, 13, 14, 15, 41, 42, 43, 62, 63, 64, 65, 77, 78, 79, 94, 95, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 119, 120, 121, 122, 123, 127, 128, 129, 130, 131, 157, 183, 184, 185, 186, 187, 193, 194, 195, 196, 197, 198, 199, 200, 201, 202, 203, 204, 208, 209, 210, 211, 212, 213, 214, 215, 216, 217, 243, 244, 245, 246, 247, 288, 289, 290, 291, 292, 344, 345, 346, 347, 348, 374, 375, 423, 453, 454, 455, 456, 457, 458, 459, 460, 461, 462, 463, 464, 470, 471, 472, 473, 474, 486, 487, 488, 489, 490, 491, 492, 493, 494, 495, 496, 497, 498, 499, 500, 501, 502, 503, 504, 505, 538, 539, 540, 541, 542, 543, 544, 545, 546, 547, 548, 549, 550, 551, 676, 677, 678, 679, 680, 694, 695, 696, 697, 698, 699, 700, 701, 702, 703, 704, 705, 706, 707, 708, 709, 710, 711, 712, 713, 768, 769, 770, 771, 772, 773, 774, 775, 776, 777, 778, 779, 780, 781, 782, 790],
    "MAP": [7, 8, 9, 10, 16, 17, 18, 19, 20, 32, 33, 34, 35, 36, 37, 38, 39, 40, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 70, 71, 72, 73, 74, 75, 76, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 98, 99, 100, 101, 137, 138, 139, 140, 151, 152, 153, 154, 155, 218, 219, 220, 221, 222, 223, 224, 236, 237, 248, 249, 250, 251, 252, 253, 254, 255, 256, 257, 287, 356, 363, 364, 365, 366, 367, 369, 370, 371, 372, 373, 377, 378, 379, 380, 381, 382, 383, 757, 758, 761, 762, 763, 764, 765, 766, 767],
    "SHOPPING": [21, 22, 23, 24, 25, 26, 47, 48, 49, 50, 51, 96, 117, 118, 124, 125, 126, 141, 142, 143, 144, 145, 146, 147, 148, 149, 150, 158, 159, 160, 161, 162, 163, 164, 165, 166, 167, 188, 189, 190, 191, 192, 225, 226, 227, 228, 229, 230, 231, 232, 233, 234, 235, 238, 239, 240, 241, 242, 260, 261, 262, 263, 264, 269, 270, 271, 272, 273, 274, 275, 276, 277, 278, 279, 280, 281, 282, 283, 284, 285, 286, 298, 299, 300, 301, 302, 313, 319, 320, 321, 322, 323, 324, 325, 326, 327, 328, 329, 330, 331, 332, 333, 334, 335, 336, 337, 338, 351, 352, 353, 354, 355, 358, 359, 360, 361, 362, 368, 376, 384, 385, 386, 387, 388, 431, 432, 433, 434, 435, 436, 437, 438, 439, 440, 465, 466, 467, 468, 469, 506, 507, 508, 509, 510, 511, 512, 513, 514, 515, 516, 517, 518, 519, 520, 521, 528, 529, 530, 531, 532, 571, 572, 573, 574, 575, 585, 586, 587, 588, 589, 653, 654, 655, 656, 657, 689, 690, 691, 692, 693, 792, 793, 794, 795, 796, 797, 798],
    "REDDIT": [27, 28, 29, 30, 31, 66, 67, 68, 69, 399, 400, 401, 402, 403, 404, 405, 406, 407, 408, 409, 410, 580, 581, 582, 583, 584, 595, 596, 597, 598, 599, 600, 601, 602, 603, 604, 605, 606, 607, 608, 609, 610, 611, 612, 613, 614, 615, 616, 617, 618, 619, 620, 621, 622, 623, 624, 625, 626, 627, 628, 629, 630, 631, 632, 633, 634, 635, 636, 637, 638, 639, 640, 641, 642, 643, 644, 645, 646, 647, 648, 649, 650, 651, 652, 714, 715, 716, 717, 718, 719, 720, 721, 722, 723, 724, 725, 726, 727, 728, 729, 730, 731, 732, 733, 734, 735],
    "GITLAB": [44, 45, 46, 102, 103, 104, 105, 106, 132, 133, 134, 135, 136, 156, 168, 169, 170, 171, 172, 173, 174, 175, 176, 177, 178, 179, 180, 181, 182, 205, 206, 207, 258, 259, 293, 294, 295, 296, 297, 303, 304, 305, 306, 307, 308, 309, 310, 311, 312, 314, 315, 316, 317, 318, 339, 340, 341, 342, 343, 349, 350, 357, 389, 390, 391, 392, 393, 394, 395, 396, 397, 398, 411, 412, 413, 414, 415, 416, 417, 418, 419, 420, 421, 422, 441, 442, 443, 444, 445, 446, 447, 448, 449, 450, 451, 452, 475, 476, 477, 478, 479, 480, 481, 482, 483, 484, 485, 522, 523, 524, 525, 526, 527, 533, 534, 535, 536, 537, 567, 568, 569, 570, 576, 577, 578, 579, 590, 591, 592, 593, 594, 658, 659, 660, 661, 662, 663, 664, 665, 666, 667, 668, 669, 670, 736, 742, 743, 744, 745, 746, 747, 748, 749, 750, 751, 752, 753, 754, 755, 756, 783, 784, 785, 786, 787, 788, 789, 799, 800, 801, 802, 803, 804, 805, 806, 807, 808, 809, 810, 811],
    "MULTISITE": [97, 265, 266, 267, 268, 424, 425, 426, 427, 428, 429, 430, 552, 553, 554, 555, 556, 557, 558, 559, 560, 561, 562, 563, 564, 565, 566, 671, 672, 673, 674, 675, 681, 682, 683, 684, 685, 686, 687, 688, 737, 738, 739, 740, 741, 759, 760, 791],
}

MERGED_SITE_TASK_ID_DICT = {
    "ALL": list(range(812)),
    "SHOPPING_ADMIN": [0, 1, 2, 3, 4, 5, 6, 11, 12, 13, 14, 15, 41, 42, 43, 62, 63, 64, 65, 77, 78, 79, 94, 95, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 119, 120, 121, 122, 123, 127, 128, 129, 130, 131, 157, 183, 184, 185, 186, 187, 193, 194, 195, 196, 197, 198, 199, 200, 201, 202, 203, 204, 208, 209, 210, 211, 212, 213, 214, 215, 216, 217, 243, 244, 245, 246, 247, 288, 289, 290, 291, 292, 344, 345, 346, 347, 348, 374, 375, 423, 453, 454, 455, 456, 457, 458, 459, 460, 461, 462, 463, 464, 470, 471, 472, 473, 474, 486, 487, 488, 489, 490, 491, 492, 493, 494, 495, 496, 497, 498, 499, 500, 501, 502, 503, 504, 505, 538, 539, 540, 541, 542, 543, 544, 545, 546, 547, 548, 549, 550, 551, 676, 677, 678, 679, 680, 694, 695, 696, 697, 698, 699, 700, 701, 702, 703, 704, 705, 706, 707, 708, 709, 710, 711, 712, 713, 768, 769, 770, 771, 772, 773, 774, 775, 776, 777, 778, 779, 780, 781, 782, 790],
    "MAP": [7, 8, 9, 10, 16, 17, 18, 19, 20, 32, 33, 34, 35, 36, 37, 38, 39, 40, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 70, 71, 72, 73, 74, 75, 76, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 97, 98, 99, 100, 101, 137, 138, 139, 140, 151, 152, 153, 154, 155, 218, 219, 220, 221, 222, 223, 224, 236, 237, 248, 249, 250, 251, 252, 253, 254, 255, 256, 257, 265, 266, 267, 268, 287, 356, 363, 364, 365, 366, 367, 369, 370, 371, 372, 373, 377, 378, 379, 380, 381, 382, 383, 424, 425, 426, 427, 428, 429, 430, 737, 738, 739, 740, 741, 757, 758, 759, 760, 761, 762, 763, 764, 765, 766, 767],
    "SHOPPING": [21, 22, 23, 24, 25, 26, 47, 48, 49, 50, 51, 96, 117, 118, 124, 125, 126, 141, 142, 143, 144, 145, 146, 147, 148, 149, 150, 158, 159, 160, 161, 162, 163, 164, 165, 166, 167, 188, 189, 190, 191, 192, 225, 226, 227, 228, 229, 230, 231, 232, 233, 234, 235, 238, 239, 240, 241, 242, 260, 261, 262, 263, 264, 269, 270, 271, 272, 273, 274, 275, 276, 277, 278, 279, 280, 281, 282, 283, 284, 285, 286, 298, 299, 300, 301, 302, 313, 319, 320, 321, 322, 323, 324, 325, 326, 327, 328, 329, 330, 331, 332, 333, 334, 335, 336, 337, 338, 351, 352, 353, 354, 355, 358, 359, 360, 361, 362, 368, 376, 384, 385, 386, 387, 388, 431, 432, 433, 434, 435, 436, 437, 438, 439, 440, 465, 466, 467, 468, 469, 506, 507, 508, 509, 510, 511, 512, 513, 514, 515, 516, 517, 518, 519, 520, 521, 528, 529, 530, 531, 532, 571, 572, 573, 574, 575, 585, 586, 587, 588, 589, 653, 654, 655, 656, 657, 671, 672, 673, 674, 675, 689, 690, 691, 692, 693, 792, 793, 794, 795, 796, 797, 798],
    "REDDIT": [27, 28, 29, 30, 31, 66, 67, 68, 69, 399, 400, 401, 402, 403, 404, 405, 406, 407, 408, 409, 410, 580, 581, 582, 583, 584, 595, 596, 597, 598, 599, 600, 601, 602, 603, 604, 605, 606, 607, 608, 609, 610, 611, 612, 613, 614, 615, 616, 617, 618, 619, 620, 621, 622, 623, 624, 625, 626, 627, 628, 629, 630, 631, 632, 633, 634, 635, 636, 637, 638, 639, 640, 641, 642, 643, 644, 645, 646, 647, 648, 649, 650, 651, 652, 681, 682, 683, 684, 685, 686, 687, 688, 714, 715, 716, 717, 718, 719, 720, 721, 722, 723, 724, 725, 726, 727, 728, 729, 730, 731, 732, 733, 734, 735],
    "GITLAB": [44, 45, 46, 102, 103, 104, 105, 106, 132, 133, 134, 135, 136, 156, 168, 169, 170, 171, 172, 173, 174, 175, 176, 177, 178, 179, 180, 181, 182, 205, 206, 207, 258, 259, 293, 294, 295, 296, 297, 303, 304, 305, 306, 307, 308, 309, 310, 311, 312, 314, 315, 316, 317, 318, 339, 340, 341, 342, 343, 349, 350, 357, 389, 390, 391, 392, 393, 394, 395, 396, 397, 398, 411, 412, 413, 414, 415, 416, 417, 418, 419, 420, 421, 422, 441, 442, 443, 444, 445, 446, 447, 448, 449, 450, 451, 452, 475, 476, 477, 478, 479, 480, 481, 482, 483, 484, 485, 522, 523, 524, 525, 526, 527, 533, 534, 535, 536, 537, 552, 553, 554, 555, 556, 557, 558, 559, 560, 561, 562, 563, 564, 565, 566, 567, 568, 569, 570, 576, 577, 578, 579, 590, 591, 592, 593, 594, 658, 659, 660, 661, 662, 663, 664, 665, 666, 667, 668, 669, 670, 736, 742, 743, 744, 745, 746, 747, 748, 749, 750, 751, 752, 753, 754, 755, 756, 783, 784, 785, 786, 787, 788, 789, 791, 799, 800, 801, 802, 803, 804, 805, 806, 807, 808, 809, 810, 811]
}

TASK_LABELS = ['shopping_admin', 'shopping_admin', 'shopping_admin', 'shopping_admin', 'shopping_admin', 'shopping_admin', 'shopping_admin', 'map', 'map', 'map', 'map', 'shopping_admin', 'shopping_admin', 'shopping_admin', 'shopping_admin', 'shopping_admin', 'map', 'map', 'map', 'map', 'map', 'shopping', 'shopping', 'shopping', 'shopping', 'shopping', 'shopping', 'reddit', 'reddit', 'reddit', 'reddit', 'reddit', 'map', 'map', 'map', 'map', 'map', 'map', 'map', 'map', 'map', 'shopping_admin', 'shopping_admin', 'shopping_admin', 'gitlab', 'gitlab', 'gitlab', 'shopping', 'shopping', 'shopping', 'shopping', 'shopping', 'map', 'map', 'map', 'map', 'map', 'map', 'map', 'map', 'map', 'map', 'shopping_admin', 'shopping_admin', 'shopping_admin', 'shopping_admin', 'reddit', 'reddit', 'reddit', 'reddit', 'map', 'map', 'map', 'map', 'map', 'map', 'map', 'shopping_admin', 'shopping_admin', 'shopping_admin', 'map', 'map', 'map', 'map', 'map', 'map', 'map', 'map', 'map', 'map', 'map', 'map', 'map', 'map', 'shopping_admin', 'shopping_admin', 'shopping', 'map', 'map', 'map', 'map', 'map', 'gitlab', 'gitlab', 'gitlab', 'gitlab', 'gitlab', 'shopping_admin', 'shopping_admin', 'shopping_admin', 'shopping_admin', 'shopping_admin', 'shopping_admin', 'shopping_admin', 'shopping_admin', 'shopping_admin', 'shopping_admin', 'shopping', 'shopping', 'shopping_admin', 'shopping_admin', 'shopping_admin', 'shopping_admin', 'shopping_admin', 'shopping', 'shopping', 'shopping', 'shopping_admin', 'shopping_admin', 'shopping_admin', 'shopping_admin', 'shopping_admin', 'gitlab', 'gitlab', 'gitlab', 'gitlab', 'gitlab', 'map', 'map', 'map', 'map', 'shopping', 'shopping', 'shopping', 'shopping', 'shopping', 'shopping', 'shopping', 'shopping', 'shopping', 'shopping', 'map', 'map', 'map', 'map', 'map', 'gitlab', 'shopping_admin', 'shopping', 'shopping', 'shopping', 'shopping', 'shopping', 'shopping', 'shopping', 'shopping', 'shopping', 'shopping', 'gitlab', 'gitlab', 'gitlab', 'gitlab', 'gitlab', 'gitlab', 'gitlab', 'gitlab', 'gitlab', 'gitlab', 'gitlab', 'gitlab', 'gitlab', 'gitlab', 'gitlab', 'shopping_admin', 'shopping_admin', 'shopping_admin', 'shopping_admin', 'shopping_admin', 'shopping', 'shopping', 'shopping', 'shopping', 'shopping', 'shopping_admin', 'shopping_admin', 'shopping_admin', 'shopping_admin', 'shopping_admin', 'shopping_admin', 'shopping_admin', 'shopping_admin', 'shopping_admin', 'shopping_admin', 'shopping_admin', 'shopping_admin', 'gitlab', 'gitlab', 'gitlab', 'shopping_admin', 'shopping_admin', 'shopping_admin', 'shopping_admin', 'shopping_admin', 'shopping_admin', 'shopping_admin', 'shopping_admin', 'shopping_admin', 'shopping_admin', 'map', 'map', 'map', 'map', 'map', 'map', 'map', 'shopping', 'shopping', 'shopping', 'shopping', 'shopping', 'shopping', 'shopping', 'shopping', 'shopping', 'shopping', 'shopping', 'map', 'map', 'shopping', 'shopping', 'shopping', 'shopping', 'shopping', 'shopping_admin', 'shopping_admin', 'shopping_admin', 'shopping_admin', 'shopping_admin', 'map', 'map', 'map', 'map', 'map', 'map', 'map', 'map', 'map', 'map', 'gitlab', 'gitlab', 'shopping', 'shopping', 'shopping', 'shopping', 'shopping', 'map', 'map', 'map', 'map', 'shopping', 'shopping', 'shopping', 'shopping', 'shopping', 'shopping', 'shopping', 'shopping', 'shopping', 'shopping', 'shopping', 'shopping', 'shopping', 'shopping', 'shopping', 'shopping', 'shopping', 'shopping', 'map', 'shopping_admin', 'shopping_admin', 'shopping_admin', 'shopping_admin', 'shopping_admin', 'gitlab', 'gitlab', 'gitlab', 'gitlab', 'gitlab', 'shopping', 'shopping', 'shopping', 'shopping', 'shopping', 'gitlab', 'gitlab', 'gitlab', 'gitlab', 'gitlab', 'gitlab', 'gitlab', 'gitlab', 'gitlab', 'gitlab', 'shopping', 'gitlab', 'gitlab', 'gitlab', 'gitlab', 'gitlab', 'shopping', 'shopping', 'shopping', 'shopping', 'shopping', 'shopping', 'shopping', 'shopping', 'shopping', 'shopping', 'shopping', 'shopping', 'shopping', 'shopping', 'shopping', 'shopping', 'shopping', 'shopping', 'shopping', 'shopping', 'gitlab', 'gitlab', 'gitlab', 'gitlab', 'gitlab', 'shopping_admin', 'shopping_admin', 'shopping_admin', 'shopping_admin', 'shopping_admin', 'gitlab', 'gitlab', 'shopping', 'shopping', 'shopping', 'shopping', 'shopping', 'map', 'gitlab', 'shopping', 'shopping', 'shopping', 'shopping', 'shopping', 'map', 'map', 'map', 'map', 'map', 'shopping', 'map', 'map', 'map', 'map', 'map', 'shopping_admin', 'shopping_admin', 'shopping', 'map', 'map', 'map', 'map', 'map', 'map', 'map', 'shopping', 'shopping', 'shopping', 'shopping', 'shopping', 'gitlab', 'gitlab', 'gitlab', 'gitlab', 'gitlab', 'gitlab', 'gitlab', 'gitlab', 'gitlab', 'gitlab', 'reddit', 'reddit', 'reddit', 'reddit', 'reddit', 'reddit', 'reddit', 'reddit', 'reddit', 'reddit', 'reddit', 'reddit', 'gitlab', 'gitlab', 'gitlab', 'gitlab', 'gitlab', 'gitlab', 'gitlab', 'gitlab', 'gitlab', 'gitlab', 'gitlab', 'gitlab', 'shopping_admin', 'map', 'map', 'map', 'map', 'map', 'map', 'map', 'shopping', 'shopping', 'shopping', 'shopping', 'shopping', 'shopping', 'shopping', 'shopping', 'shopping', 'shopping', 'gitlab', 'gitlab', 'gitlab', 'gitlab', 'gitlab', 'gitlab', 'gitlab', 'gitlab', 'gitlab', 'gitlab', 'gitlab', 'gitlab', 'shopping_admin', 'shopping_admin', 'shopping_admin', 'shopping_admin', 'shopping_admin', 'shopping_admin', 'shopping_admin', 'shopping_admin', 'shopping_admin', 'shopping_admin', 'shopping_admin', 'shopping_admin', 'shopping', 'shopping', 'shopping', 'shopping', 'shopping', 'shopping_admin', 'shopping_admin', 'shopping_admin', 'shopping_admin', 'shopping_admin', 'gitlab', 'gitlab', 'gitlab', 'gitlab', 'gitlab', 'gitlab', 'gitlab', 'gitlab', 'gitlab', 'gitlab', 'gitlab', 'shopping_admin', 'shopping_admin', 'shopping_admin', 'shopping_admin', 'shopping_admin', 'shopping_admin', 'shopping_admin', 'shopping_admin', 'shopping_admin', 'shopping_admin', 'shopping_admin', 'shopping_admin', 'shopping_admin', 'shopping_admin', 'shopping_admin', 'shopping_admin', 'shopping_admin', 'shopping_admin', 'shopping_admin', 'shopping_admin', 'shopping', 'shopping', 'shopping', 'shopping', 'shopping', 'shopping', 'shopping', 'shopping', 'shopping', 'shopping', 'shopping', 'shopping', 'shopping', 'shopping', 'shopping', 'shopping', 'gitlab', 'gitlab', 'gitlab', 'gitlab', 'gitlab', 'gitlab', 'shopping', 'shopping', 'shopping', 'shopping', 'shopping', 'gitlab', 'gitlab', 'gitlab', 'gitlab', 'gitlab', 'shopping_admin', 'shopping_admin', 'shopping_admin', 'shopping_admin', 'shopping_admin', 'shopping_admin', 'shopping_admin', 'shopping_admin', 'shopping_admin', 'shopping_admin', 'shopping_admin', 'shopping_admin', 'shopping_admin', 'shopping_admin', 'gitlab', 'gitlab', 'gitlab', 'gitlab', 'gitlab', 'gitlab', 'gitlab', 'gitlab', 'gitlab', 'gitlab', 'gitlab', 'gitlab', 'gitlab', 'gitlab', 'gitlab', 'gitlab', 'gitlab', 'gitlab', 'gitlab', 'shopping', 'shopping', 'shopping', 'shopping', 'shopping', 'gitlab', 'gitlab', 'gitlab', 'gitlab', 'reddit', 'reddit', 'reddit', 'reddit', 'reddit', 'shopping', 'shopping', 'shopping', 'shopping', 'shopping', 'gitlab', 'gitlab', 'gitlab', 'gitlab', 'gitlab', 'reddit', 'reddit', 'reddit', 'reddit', 'reddit', 'reddit', 'reddit', 'reddit', 'reddit', 'reddit', 'reddit', 'reddit', 'reddit', 'reddit', 'reddit', 'reddit', 'reddit', 'reddit', 'reddit', 'reddit', 'reddit', 'reddit', 'reddit', 'reddit', 'reddit', 'reddit', 'reddit', 'reddit', 'reddit', 'reddit', 'reddit', 'reddit', 'reddit', 'reddit', 'reddit', 'reddit', 'reddit', 'reddit', 'reddit', 'reddit', 'reddit', 'reddit', 'reddit', 'reddit', 'reddit', 'reddit', 'reddit', 'reddit', 'reddit', 'reddit', 'reddit', 'reddit', 'reddit', 'reddit', 'reddit', 'reddit', 'reddit', 'reddit', 'shopping', 'shopping', 'shopping', 'shopping', 'shopping', 'gitlab', 'gitlab', 'gitlab', 'gitlab', 'gitlab', 'gitlab', 'gitlab', 'gitlab', 'gitlab', 'gitlab', 'gitlab', 'gitlab', 'gitlab', 'shopping', 'shopping', 'shopping', 'shopping', 'shopping', 'shopping_admin', 'shopping_admin', 'shopping_admin', 'shopping_admin', 'shopping_admin', 'reddit', 'reddit', 'reddit', 'reddit', 'reddit', 'reddit', 'reddit', 'reddit', 'shopping', 'shopping', 'shopping', 'shopping', 'shopping', 'shopping_admin', 'shopping_admin', 'shopping_admin', 'shopping_admin', 'shopping_admin', 'shopping_admin', 'shopping_admin', 'shopping_admin', 'shopping_admin', 'shopping_admin', 'shopping_admin', 'shopping_admin', 'shopping_admin', 'shopping_admin', 'shopping_admin', 'shopping_admin', 'shopping_admin', 'shopping_admin', 'shopping_admin', 'shopping_admin', 'reddit', 'reddit', 'reddit', 'reddit', 'reddit', 'reddit', 'reddit', 'reddit', 'reddit', 'reddit', 'reddit', 'reddit', 'reddit', 'reddit', 'reddit', 'reddit', 'reddit', 'reddit', 'reddit', 'reddit', 'reddit', 'reddit', 'gitlab', 'map', 'map', 'map', 'map', 'map', 'gitlab', 'gitlab', 'gitlab', 'gitlab', 'gitlab', 'gitlab', 'gitlab', 'gitlab', 'gitlab', 'gitlab', 'gitlab', 'gitlab', 'gitlab', 'gitlab', 'gitlab', 'map', 'map', 'map', 'map', 'map', 'map', 'map', 'map', 'map', 'map', 'map', 'shopping_admin', 'shopping_admin', 'shopping_admin', 'shopping_admin', 'shopping_admin', 'shopping_admin', 'shopping_admin', 'shopping_admin', 'shopping_admin', 'shopping_admin', 'shopping_admin', 'shopping_admin', 'shopping_admin', 'shopping_admin', 'shopping_admin', 'gitlab', 'gitlab', 'gitlab', 'gitlab', 'gitlab', 'gitlab', 'gitlab', 'shopping_admin', 'gitlab', 'shopping', 'shopping', 'shopping', 'shopping', 'shopping', 'shopping', 'shopping', 'gitlab', 'gitlab', 'gitlab', 'gitlab', 'gitlab', 'gitlab', 'gitlab', 'gitlab', 'gitlab', 'gitlab', 'gitlab', 'gitlab', 'gitlab']
TASK_LABELS_MULTISITE = ['shopping_admin', 'shopping_admin', 'shopping_admin', 'shopping_admin', 'shopping_admin', 'shopping_admin', 'shopping_admin', 'map', 'map', 'map', 'map', 'shopping_admin', 'shopping_admin', 'shopping_admin', 'shopping_admin', 'shopping_admin', 'map', 'map', 'map', 'map', 'map', 'shopping', 'shopping', 'shopping', 'shopping', 'shopping', 'shopping', 'reddit', 'reddit', 'reddit', 'reddit', 'reddit', 'map', 'map', 'map', 'map', 'map', 'map', 'map', 'map', 'map', 'shopping_admin', 'shopping_admin', 'shopping_admin', 'gitlab', 'gitlab', 'gitlab', 'shopping', 'shopping', 'shopping', 'shopping', 'shopping', 'map', 'map', 'map', 'map', 'map', 'map', 'map', 'map', 'map', 'map', 'shopping_admin', 'shopping_admin', 'shopping_admin', 'shopping_admin', 'reddit', 'reddit', 'reddit', 'reddit', 'map', 'map', 'map', 'map', 'map', 'map', 'map', 'shopping_admin', 'shopping_admin', 'shopping_admin', 'map', 'map', 'map', 'map', 'map', 'map', 'map', 'map', 'map', 'map', 'map', 'map', 'map', 'map', 'shopping_admin', 'shopping_admin', 'shopping', 'multisite', 'map', 'map', 'map', 'map', 'gitlab', 'gitlab', 'gitlab', 'gitlab', 'gitlab', 'shopping_admin', 'shopping_admin', 'shopping_admin', 'shopping_admin', 'shopping_admin', 'shopping_admin', 'shopping_admin', 'shopping_admin', 'shopping_admin', 'shopping_admin', 'shopping', 'shopping', 'shopping_admin', 'shopping_admin', 'shopping_admin', 'shopping_admin', 'shopping_admin', 'shopping', 'shopping', 'shopping', 'shopping_admin', 'shopping_admin', 'shopping_admin', 'shopping_admin', 'shopping_admin', 'gitlab', 'gitlab', 'gitlab', 'gitlab', 'gitlab', 'map', 'map', 'map', 'map', 'shopping', 'shopping', 'shopping', 'shopping', 'shopping', 'shopping', 'shopping', 'shopping', 'shopping', 'shopping', 'map', 'map', 'map', 'map', 'map', 'gitlab', 'shopping_admin', 'shopping', 'shopping', 'shopping', 'shopping', 'shopping', 'shopping', 'shopping', 'shopping', 'shopping', 'shopping', 'gitlab', 'gitlab', 'gitlab', 'gitlab', 'gitlab', 'gitlab', 'gitlab', 'gitlab', 'gitlab', 'gitlab', 'gitlab', 'gitlab', 'gitlab', 'gitlab', 'gitlab', 'shopping_admin', 'shopping_admin', 'shopping_admin', 'shopping_admin', 'shopping_admin', 'shopping', 'shopping', 'shopping', 'shopping', 'shopping', 'shopping_admin', 'shopping_admin', 'shopping_admin', 'shopping_admin', 'shopping_admin', 'shopping_admin', 'shopping_admin', 'shopping_admin', 'shopping_admin', 'shopping_admin', 'shopping_admin', 'shopping_admin', 'gitlab', 'gitlab', 'gitlab', 'shopping_admin', 'shopping_admin', 'shopping_admin', 'shopping_admin', 'shopping_admin', 'shopping_admin', 'shopping_admin', 'shopping_admin', 'shopping_admin', 'shopping_admin', 'map', 'map', 'map', 'map', 'map', 'map', 'map', 'shopping', 'shopping', 'shopping', 'shopping', 'shopping', 'shopping', 'shopping', 'shopping', 'shopping', 'shopping', 'shopping', 'map', 'map', 'shopping', 'shopping', 'shopping', 'shopping', 'shopping', 'shopping_admin', 'shopping_admin', 'shopping_admin', 'shopping_admin', 'shopping_admin', 'map', 'map', 'map', 'map', 'map', 'map', 'map', 'map', 'map', 'map', 'gitlab', 'gitlab', 'shopping', 'shopping', 'shopping', 'shopping', 'shopping', 'multisite', 'multisite', 'multisite', 'multisite', 'shopping', 'shopping', 'shopping', 'shopping', 'shopping', 'shopping', 'shopping', 'shopping', 'shopping', 'shopping', 'shopping', 'shopping', 'shopping', 'shopping', 'shopping', 'shopping', 'shopping', 'shopping', 'map', 'shopping_admin', 'shopping_admin', 'shopping_admin', 'shopping_admin', 'shopping_admin', 'gitlab', 'gitlab', 'gitlab', 'gitlab', 'gitlab', 'shopping', 'shopping', 'shopping', 'shopping', 'shopping', 'gitlab', 'gitlab', 'gitlab', 'gitlab', 'gitlab', 'gitlab', 'gitlab', 'gitlab', 'gitlab', 'gitlab', 'shopping', 'gitlab', 'gitlab', 'gitlab', 'gitlab', 'gitlab', 'shopping', 'shopping', 'shopping', 'shopping', 'shopping', 'shopping', 'shopping', 'shopping', 'shopping', 'shopping', 'shopping', 'shopping', 'shopping', 'shopping', 'shopping', 'shopping', 'shopping', 'shopping', 'shopping', 'shopping', 'gitlab', 'gitlab', 'gitlab', 'gitlab', 'gitlab', 'shopping_admin', 'shopping_admin', 'shopping_admin', 'shopping_admin', 'shopping_admin', 'gitlab', 'gitlab', 'shopping', 'shopping', 'shopping', 'shopping', 'shopping', 'map', 'gitlab', 'shopping', 'shopping', 'shopping', 'shopping', 'shopping', 'map', 'map', 'map', 'map', 'map', 'shopping', 'map', 'map', 'map', 'map', 'map', 'shopping_admin', 'shopping_admin', 'shopping', 'map', 'map', 'map', 'map', 'map', 'map', 'map', 'shopping', 'shopping', 'shopping', 'shopping', 'shopping', 'gitlab', 'gitlab', 'gitlab', 'gitlab', 'gitlab', 'gitlab', 'gitlab', 'gitlab', 'gitlab', 'gitlab', 'reddit', 'reddit', 'reddit', 'reddit', 'reddit', 'reddit', 'reddit', 'reddit', 'reddit', 'reddit', 'reddit', 'reddit', 'gitlab', 'gitlab', 'gitlab', 'gitlab', 'gitlab', 'gitlab', 'gitlab', 'gitlab', 'gitlab', 'gitlab', 'gitlab', 'gitlab', 'shopping_admin', 'multisite', 'multisite', 'multisite', 'multisite', 'multisite', 'multisite', 'multisite', 'shopping', 'shopping', 'shopping', 'shopping', 'shopping', 'shopping', 'shopping', 'shopping', 'shopping', 'shopping', 'gitlab', 'gitlab', 'gitlab', 'gitlab', 'gitlab', 'gitlab', 'gitlab', 'gitlab', 'gitlab', 'gitlab', 'gitlab', 'gitlab', 'shopping_admin', 'shopping_admin', 'shopping_admin', 'shopping_admin', 'shopping_admin', 'shopping_admin', 'shopping_admin', 'shopping_admin', 'shopping_admin', 'shopping_admin', 'shopping_admin', 'shopping_admin', 'shopping', 'shopping', 'shopping', 'shopping', 'shopping', 'shopping_admin', 'shopping_admin', 'shopping_admin', 'shopping_admin', 'shopping_admin', 'gitlab', 'gitlab', 'gitlab', 'gitlab', 'gitlab', 'gitlab', 'gitlab', 'gitlab', 'gitlab', 'gitlab', 'gitlab', 'shopping_admin', 'shopping_admin', 'shopping_admin', 'shopping_admin', 'shopping_admin', 'shopping_admin', 'shopping_admin', 'shopping_admin', 'shopping_admin', 'shopping_admin', 'shopping_admin', 'shopping_admin', 'shopping_admin', 'shopping_admin', 'shopping_admin', 'shopping_admin', 'shopping_admin', 'shopping_admin', 'shopping_admin', 'shopping_admin', 'shopping', 'shopping', 'shopping', 'shopping', 'shopping', 'shopping', 'shopping', 'shopping', 'shopping', 'shopping', 'shopping', 'shopping', 'shopping', 'shopping', 'shopping', 'shopping', 'gitlab', 'gitlab', 'gitlab', 'gitlab', 'gitlab', 'gitlab', 'shopping', 'shopping', 'shopping', 'shopping', 'shopping', 'gitlab', 'gitlab', 'gitlab', 'gitlab', 'gitlab', 'shopping_admin', 'shopping_admin', 'shopping_admin', 'shopping_admin', 'shopping_admin', 'shopping_admin', 'shopping_admin', 'shopping_admin', 'shopping_admin', 'shopping_admin', 'shopping_admin', 'shopping_admin', 'shopping_admin', 'shopping_admin', 'multisite', 'multisite', 'multisite', 'multisite', 'multisite', 'multisite', 'multisite', 'multisite', 'multisite', 'multisite', 'multisite', 'multisite', 'multisite', 'multisite', 'multisite', 'gitlab', 'gitlab', 'gitlab', 'gitlab', 'shopping', 'shopping', 'shopping', 'shopping', 'shopping', 'gitlab', 'gitlab', 'gitlab', 'gitlab', 'reddit', 'reddit', 'reddit', 'reddit', 'reddit', 'shopping', 'shopping', 'shopping', 'shopping', 'shopping', 'gitlab', 'gitlab', 'gitlab', 'gitlab', 'gitlab', 'reddit', 'reddit', 'reddit', 'reddit', 'reddit', 'reddit', 'reddit', 'reddit', 'reddit', 'reddit', 'reddit', 'reddit', 'reddit', 'reddit', 'reddit', 'reddit', 'reddit', 'reddit', 'reddit', 'reddit', 'reddit', 'reddit', 'reddit', 'reddit', 'reddit', 'reddit', 'reddit', 'reddit', 'reddit', 'reddit', 'reddit', 'reddit', 'reddit', 'reddit', 'reddit', 'reddit', 'reddit', 'reddit', 'reddit', 'reddit', 'reddit', 'reddit', 'reddit', 'reddit', 'reddit', 'reddit', 'reddit', 'reddit', 'reddit', 'reddit', 'reddit', 'reddit', 'reddit', 'reddit', 'reddit', 'reddit', 'reddit', 'reddit', 'shopping', 'shopping', 'shopping', 'shopping', 'shopping', 'gitlab', 'gitlab', 'gitlab', 'gitlab', 'gitlab', 'gitlab', 'gitlab', 'gitlab', 'gitlab', 'gitlab', 'gitlab', 'gitlab', 'gitlab', 'multisite', 'multisite', 'multisite', 'multisite', 'multisite', 'shopping_admin', 'shopping_admin', 'shopping_admin', 'shopping_admin', 'shopping_admin', 'multisite', 'multisite', 'multisite', 'multisite', 'multisite', 'multisite', 'multisite', 'multisite', 'shopping', 'shopping', 'shopping', 'shopping', 'shopping', 'shopping_admin', 'shopping_admin', 'shopping_admin', 'shopping_admin', 'shopping_admin', 'shopping_admin', 'shopping_admin', 'shopping_admin', 'shopping_admin', 'shopping_admin', 'shopping_admin', 'shopping_admin', 'shopping_admin', 'shopping_admin', 'shopping_admin', 'shopping_admin', 'shopping_admin', 'shopping_admin', 'shopping_admin', 'shopping_admin', 'reddit', 'reddit', 'reddit', 'reddit', 'reddit', 'reddit', 'reddit', 'reddit', 'reddit', 'reddit', 'reddit', 'reddit', 'reddit', 'reddit', 'reddit', 'reddit', 'reddit', 'reddit', 'reddit', 'reddit', 'reddit', 'reddit', 'gitlab', 'multisite', 'multisite', 'multisite', 'multisite', 'multisite', 'gitlab', 'gitlab', 'gitlab', 'gitlab', 'gitlab', 'gitlab', 'gitlab', 'gitlab', 'gitlab', 'gitlab', 'gitlab', 'gitlab', 'gitlab', 'gitlab', 'gitlab', 'map', 'map', 'multisite', 'multisite', 'map', 'map', 'map', 'map', 'map', 'map', 'map', 'shopping_admin', 'shopping_admin', 'shopping_admin', 'shopping_admin', 'shopping_admin', 'shopping_admin', 'shopping_admin', 'shopping_admin', 'shopping_admin', 'shopping_admin', 'shopping_admin', 'shopping_admin', 'shopping_admin', 'shopping_admin', 'shopping_admin', 'gitlab', 'gitlab', 'gitlab', 'gitlab', 'gitlab', 'gitlab', 'gitlab', 'shopping_admin', 'multisite', 'shopping', 'shopping', 'shopping', 'shopping', 'shopping', 'shopping', 'shopping', 'gitlab', 'gitlab', 'gitlab', 'gitlab', 'gitlab', 'gitlab', 'gitlab', 'gitlab', 'gitlab', 'gitlab', 'gitlab', 'gitlab', 'gitlab']

TOTAL_TASK_NUM_DICT = {
    "ALL": 812,
    "SHOPPING_ADMIN": 182,
    "MAP": 109,
    "SHOPPING": 187,
    "REDDIT": 106,
    "GITLAB": 180,
    "MULTISITE": 48
}

EVELUATOR_RECTIFICATIONS = [16, 17, 18, 19, 20, 97, 146, 178, 179, 180, 181, 182, 240, 254, 261, 262, 263, 264, 293, 294, 295, 296, 297, 298, 299, 300, 301, 302, 308, 309, 310, 311, 312, 330, 351, 352, 353, 354, 355, 363, 364, 365, 366, 367, 415, 416, 417, 418, 489, 528, 529, 530, 531, 532, 583, 584, 601, 603, 606, 608, 629, 640, 641, 642, 643, 644, 645, 646, 647, 648, 649, 653, 654, 655, 656, 657, 679, 707, 708, 709]

TRAJECTORY_DIR_DICT = {
    # Main Results
    0: os.path.join(TRAJECTORY_DIR, "AgentOccam"),
    1: os.path.join(TRAJECTORY_DIR, "AgentOccam-SteP"),
    2: os.path.join(TRAJECTORY_DIR, "AgentOccam-Judge"),
    # Ablation Study
    3: os.path.join(TRAJECTORY_DIR, "reduced_action"),
    4: os.path.join(TRAJECTORY_DIR, "reduced_action-X_scrolling"),
    5: os.path.join(TRAJECTORY_DIR, "reduced_action-X_scrolling-obs_opt"),
    6: os.path.join(TRAJECTORY_DIR, "reduced_action-X_scrolling-obs_opt-history"),
    # Replications
    7: os.path.join(TRAJECTORY_DIR, "WebArena-replication"),
    8: os.path.join(TRAJECTORY_DIR, "SteP-replication"),
}

RUN_NAME_DICT = {
    # Main Results
    0: "AgentOccam",
    1: "AgentOccam + SteP",
    2: "AgentOccam + Judge",
    # Ablation Study
    3: "↓ Actions",
    4: "Above + X Scrolling",
    5: "Above + Obs Opt.",
    6: "Above + History",
    # Replications
    7: "WebArena-replication",
    8: "SteP-replication",
}

COLOR_DICT = {
    # Main Results
    0: "#45C4B0",
    1: "#B68193",
    2: "#E7D5BF",
    # Ablation Study
    3: "#594D47",
    4: "#6E8480",
    5: "#D98C6C",
    6: "#997E73",
    # Replications
    7: "#203330",
    8: "#969696",
}

def print_trajectory(json_path):
    import json
    item = json.load(open(json_path, "r"))
    for step in item["trajectory"]:
        obj = step["objective"]
        url = step["url"]
        obs = step["observation"]
        reason = step["reason"]
        action = step["action"]
        if "plan" in step.keys():
            plan = step["plan"]
            print(f"### Objective\n{obj}")
            print(f"### Url\n{url}")
            print(f"### Observation\n{obs}")
            print(f"### Plan\n{plan}")
            print(f"### Reason\n{reason}")
            print(f"### Action\n{action}")
        else:
            print(f"### Objective\n{obj}")
            print(f"### Url\n{url}")
            print(f"### Observation\n{obs}")
            print(f"### Reason\n{reason}")
            print(f"### Action\n{action}")

def find_task_by_intent_template_id(intent_template_id, task_config_data_dir=EVALUATOR_DIR):
    import json
    for filename in sorted([p for p in os.listdir(task_config_data_dir) if p[0].isdigit()], key=lambda item: int(os.path.basename(item)[:-len(".json")])):
        if filename.endswith(".json"):
            filepath = os.path.join(task_config_data_dir, filename)
            with open(filepath, 'r', encoding='utf-8') as file:
                try:
                    data = json.load(file)
                    if data.get('intent_template_id') == intent_template_id:
                        intent = data.get("intent")
                        print(f"File: {filename}\nIntent: {intent}")
                except json.JSONDecodeError as e:
                    print(f"Error decoding JSON from file {filename}: {str(e)}")

def traverse_task_configs(task_config_data_dir=EVALUATOR_DIR):
    import json
    task_id_dict = {}
    for filename in sorted([p for p in os.listdir(task_config_data_dir) if p[0].isdigit()], key=lambda item: int(os.path.basename(item)[:-len(".json")])):
        if filename.endswith(".json"):
            filepath = os.path.join(task_config_data_dir, filename)
            with open(filepath, 'r', encoding='utf-8') as file:
                try:
                    data = json.load(file)
                    data_site = data["sites"][0]
                    if len(data["sites"]) > 1:
                        data_site = "multisite"
                    if data_site not in task_id_dict.keys():
                        task_id_dict[data_site] = []
                    task_id_dict[data_site].append(data["task_id"])
                except json.JSONDecodeError as e:
                    print(f"Error decoding JSON from file {filename}: {str(e)}")
    for k in task_id_dict.keys():
        print(f"\"{k.upper()}\":", "["+", ".join([str(item) for item in sorted(task_id_dict[k], reverse=False)])+"],")
    print()
    for i in range(812):
        for k in task_id_dict.keys():
            if i in task_id_dict[k]:
                print(repr(k)+", ", end="")

def load_json_obj_from_file(filepath):
    with open(filepath, 'r') as f:
        data = json.load(f)
    return data

def print_task_info_by_id(task_config_dir=EVALUATOR_DIR, task_ids=[65]):
    for task_id in task_ids:
        filepath = os.path.join(task_config_dir, f"{task_id}.json")
        task_data = load_json_obj_from_file(filepath)
        print(task_data["start_url"]) 

def clean_trajectory_files(input_dir, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    for filename in [f"{i}.json" for i in range(812)]:
        trajectory_obj = json.load(open(os.path.join(input_dir, filename), "r"))
        new_obj = {}
        for k in ["task", "id", "model"]:
            new_obj[k] =  trajectory_obj[k]
        new_obj["type"] = "observation_action_space_refinement"
        new_obj["objective"] = trajectory_obj["trajectory"][0]["objective"]
        new_obj["trajectory"] = []
        for step in range(len(trajectory_obj["trajectory"])):
            step_obj = {}
            for k in ["url", "observation", "num_actions", "plan", "interaction_history_summary", "observation_description", "reason", "action", "observation_highlight_idxs", "done"]:
                step_obj[k] = trajectory_obj["trajectory"][step][k]
            step_obj["reward"] = trajectory_obj["trajectory"][step]["reward"] if trajectory_obj["trajectory"][step]["reward"] == 1. else 0.
            new_obj["trajectory"].append(step_obj)
        json.dump(new_obj, open(os.path.join(output_dir, filename), "w"), indent=4)

def check_shopping_admin_login_expire():
    login_expire_dict = {}
    for k in set(TRAJECTORY_DIR_DICT.keys())-set({16}):
        for task_id in MERGED_SITE_TASK_ID_DICT["SHOPPING_ADMIN"]:
            filepath = os.path.join(TRAJECTORY_DIR_DICT[k], f"{task_id}.json")
            if not os.path.exists(filepath):
                print(f"{filepath} doesn't exist.")
                continue
            trajectory_data = json.load(open(filepath, 'r'))
            step_0_data = trajectory_data["trajectory"][0]
            if "username" in step_0_data["observation"].lower() and "password" in step_0_data["observation"].lower() and "sign in" in step_0_data["observation"].lower():
                if k in login_expire_dict.keys():
                    login_expire_dict[k].append(task_id)
                else:
                    login_expire_dict[k] = [task_id]
    for k in sorted(list(login_expire_dict.keys())):
        print(k)
        print(login_expire_dict[k])

def check_reddit_post_limit():
    post_limit_dict = {}
    for k in set(TRAJECTORY_DIR_DICT.keys())-set({16}):
        for task_id in MERGED_SITE_TASK_ID_DICT["REDDIT"]:
            filepath = os.path.join(TRAJECTORY_DIR_DICT[k], f"{task_id}.json")
            if not os.path.exists(filepath):
                print(f"{filepath} doesn't exist.")
                continue
            trajectory_data = json.load(open(filepath, 'r'))
            for step_data in trajectory_data["trajectory"]:
                if "You cannot post more. Wait a while before trying again." in step_data["observation"]:
                    if k in post_limit_dict.keys():
                        post_limit_dict[k].append(task_id)
                    else:
                        post_limit_dict[k] = [task_id]
                    break
    for k in sorted(list(post_limit_dict.keys())):
        print(k)
        print(post_limit_dict[k])

def get_action_statistics(trajectory_list=[-1], action_list=["click", "type"]):
    ACTION_WITH_ID_LIST = ["click", "type", "scroll", "goto", "note", "stop", "branch", "prune"]
    trial_dict = {}
    for k in trajectory_list:
        trial_dict[k] = {}
        for task_id in range(812):
            if k != 16:
                filepath = os.path.join(TRAJECTORY_DIR_DICT[k], f"{task_id}.json")
                if not os.path.exists(filepath):
                    print(f"{filepath} doesn't exist.")
                    continue
                trajectory_data = json.load(open(filepath, 'r'))
                for step_data in trajectory_data["trajectory"]:
                    for action in action_list:
                        if (action in ACTION_WITH_ID_LIST and f"{action} [" in step_data["action"]) or (action not in ACTION_WITH_ID_LIST and action in step_data["action"]):
                            if action in trial_dict[k].keys():
                                trial_dict[k][action] += 1
                            else:
                                trial_dict[k][action] = 1
            else:
                filepath = os.path.join(TRAJECTORY_DIR_DICT[k], f"trace_{task_id}.json")
                if not os.path.exists(filepath):
                    print(f"{filepath} doesn't exist.")
                    continue
                trajectory_data = json.load(open(filepath, 'r'))
                for step_data in trajectory_data["trace"]:
                    for action in action_list:
                        if (action in ACTION_WITH_ID_LIST and f"{action} [" in step_data["target"]) or (action not in ACTION_WITH_ID_LIST and action in step_data["target"]):
                            if action in trial_dict[k].keys():
                                trial_dict[k][action] += 1
                            else:
                                trial_dict[k][action] = 1
    csvfile = open(os.path.join(OUTPUT_DIR, "action_statistics.csv"), "w")
    csv_writer = csv.writer(csvfile)
    csv_writer.writerow(["TRIAL NAME"] + action_list)
    for k in trajectory_list:
        print(k)
        csv_writer.writerow([RUN_NAME_DICT[k]] + [trial_dict[k][a] if a in trial_dict[k].keys() else 0 for a in action_list])
        for a in trial_dict[k].keys():
            print(a, trial_dict[k][a])

def get_avr_obs_token_num_statistics(trajectory_list=[-1]):
    from transformers import AutoTokenizer
    tokenizer = AutoTokenizer.from_pretrained("gpt2")
    trial_dict = {}
    for k in trajectory_list:
        trial_dict[k] = {}
        for task_id in range(812):
            site_label = TASK_LABELS_MULTISITE[task_id]
            trajectory_total_token_num = 0
            if k != 16:
                filepath = os.path.join(TRAJECTORY_DIR_DICT[k], f"{task_id}.json")
                if not os.path.exists(filepath):
                    print(f"{filepath} doesn't exist.")
                    continue
                trajectory_data = json.load(open(filepath, 'r'))
                step_num = len(trajectory_data["trajectory"])
                for step_data in trajectory_data["trajectory"]:
                    trajectory_total_token_num += len(tokenizer.tokenize(step_data["observation"]))
            else:
                filepath = os.path.join(TRAJECTORY_DIR_DICT[k], f"trace_{task_id}.json")
                if not os.path.exists(filepath):
                    print(f"{filepath} doesn't exist.")
                    continue
                trajectory_data = json.load(open(filepath, 'r'))
                step_num = len(trajectory_data["trace"])
                for step_data in trajectory_data["trace"]:
                    for source_data in step_data["source"]:
                        trajectory_total_token_num += len(tokenizer.tokenize(source_data["content"]))
            print(trajectory_total_token_num, step_num)
            if site_label in trial_dict[k].keys():
                trial_dict[k][site_label]["total_token_num"] += trajectory_total_token_num
                trial_dict[k][site_label]["total_step_num"] += step_num
            else:
                trial_dict[k][site_label] = {"total_token_num": trajectory_total_token_num, "total_step_num": step_num}
            if "all" in trial_dict[k].keys():
                trial_dict[k]["all"]["total_token_num"] += trajectory_total_token_num
                trial_dict[k]["all"]["total_step_num"] += step_num
            else:
                trial_dict[k]["all"] = {"total_token_num": trajectory_total_token_num, "total_step_num": step_num}
    csvfile = open(os.path.join(OUTPUT_DIR, "avr_obs_token_num_statistics.csv"), "w")
    csv_writer = csv.writer(csvfile)
    SITES = ["ALL", "SHOPPING", "SHOPPING_ADMIN", "GITLAB", "MAP", "REDDIT", "MAP", "MULTISITE"]
    csv_writer.writerow(["TRIAL NAME"] + SITES)
    for k in trajectory_list:
        csv_writer.writerow([RUN_NAME_DICT[k]] + ["{:.1f}".format(trial_dict[k][s.lower()]["total_token_num"]/trial_dict[k][s.lower()]["total_step_num"]) for s in SITES])

def get_avr_step_num_statistics(trajectory_list=[-1]):
    trial_dict = {}
    for k in trajectory_list:
        trial_dict[k] = {}
        for task_id in range(812):
            site_label = TASK_LABELS_MULTISITE[task_id]
            if k != 16:
                filepath = os.path.join(TRAJECTORY_DIR_DICT[k], f"{task_id}.json")
                if not os.path.exists(filepath):
                    print(f"{filepath} doesn't exist.")
                    continue
                trajectory_data = json.load(open(filepath, 'r'))
                if site_label in trial_dict[k].keys():
                    trial_dict[k][site_label] += len(trajectory_data["trajectory"])
                else:
                    trial_dict[k][site_label] = len(trajectory_data["trajectory"])
                if "all" in trial_dict[k].keys():
                    trial_dict[k]["all"] += len(trajectory_data["trajectory"])
                else:
                    trial_dict[k]["all"] = len(trajectory_data["trajectory"])
            else:
                filepath = os.path.join(TRAJECTORY_DIR_DICT[k], f"trace_{task_id}.json")
                if not os.path.exists(filepath):
                    print(f"{filepath} doesn't exist.")
                    continue
                trajectory_data = json.load(open(filepath, 'r'))
                if site_label in trial_dict[k].keys():
                    trial_dict[k][site_label] += len(trajectory_data["trace"])
                else:
                    trial_dict[k][site_label] = len(trajectory_data["trace"])
                if "all" in trial_dict[k].keys():
                    trial_dict[k]["all"] += len(trajectory_data["trace"])
                else:
                    trial_dict[k]["all"] = len(trajectory_data["trace"])
    csvfile = open(os.path.join(OUTPUT_DIR, "avr_step_num_statistics.csv"), "w")
    csv_writer = csv.writer(csvfile)
    SITES = ["ALL", "SHOPPING", "SHOPPING_ADMIN", "GITLAB", "MAP", "REDDIT", "MULTISITE"]
    csv_writer.writerow(["TRIAL NAME"] + SITES)
    for k in trajectory_list:
        csv_writer.writerow([RUN_NAME_DICT[k]] + ["{:.1f}".format(trial_dict[k][s.lower()]/TOTAL_TASK_NUM_DICT[s]) for s in SITES])

def compare_evaluators(dir1, dir2):
    def compare_evaluator(i, file1, file2):
        def load_json(file_path):
            with open(file_path, 'r') as f:
                return json.load(f)
            
        def compare_json(json1, json2, path=""):
            differences = {}

            for key in json1:
                new_path = f"{path}.{key}" if path else key
                
                if key not in json2:
                    differences[new_path] = json1[key]
                else:
                    if isinstance(json1[key], dict) and isinstance(json2[key], dict):
                        nested_diff = compare_json(json1[key], json2[key], new_path)
                        differences.update(nested_diff)
                    elif json1[key] != json2[key]:
                        differences[new_path] = (json1[key], json2[key])
        
            for key in json2:
                new_path = f"{path}.{key}" if path else key
                
                if key not in json1:
                    differences[new_path] = json2[key]

            return differences
                
        json1 = load_json(file1)
        json2 = load_json(file2)
        
        differences = compare_json(json1, json2)
        
        if differences:
            print(f"# Task {i}", file=file)
            for key, value in differences.items():
                if isinstance(value, tuple):
                    print("### {}\n{}\n{}".format(key, value[0], value[1]), file=file)
                else:
                    print("### {}\n{}".format(key, value), file=file)
            print(file=file)

    file = open(os.path.join(OUTPUT_DIR, "evaluator_differences.txt"), "w")
    for i in range(812):
        file1 = os.path.join(dir1, f"{i}.json")
        file2 = os.path.join(dir2, f"{i}.json")
        compare_evaluator(i, file1, file2)

if __name__ == "__main__":
    get_action_statistics(trajectory_list=[7, 3, 4, 5, 6, 0], action_list=["click", "hover", "type", "scroll", "go_back", "goto", "note", "stop", "go_home", "branch", "prune"])