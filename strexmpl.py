# import body
# import streamlit as st
# from click import style

# page_bg-img = """
# <style>
# </style>
# """
#
# st.markdown(page_bg-img, unsafe-allow-html=True)
# st.title("It's summer!")
#
# st.markdown(body, unsafe_allow_html=False, *, help=None)


import streamlit as st

# st.markdown("*Streamlit* is **really** ***cool***.")
# st.markdown('''
#     :red[Streamlit] :orange[can] :green[write] :blue[text] :violet[in]
#     :gray[pretty] :rainbow[colors] and :blue-background[highlight] text.''')
# st.markdown("Here's a bouquet &mdash;\
#             :tulip::cherry_blossom::rose::hibiscus::sunflower::blossom:")
#
# multi = '''If you end a line with two spaces,
# a soft return is used for the next line.
#
# Two (or more) newline characters in a row will result in a hard return.
# '''
# st.markdown(multi)

import streamlit as st

md = st.text_area( "Happy Streamlit-ing! :balloon:")

# st.code(f"""
# import streamlit as st
#
# st.markdown('''{md}''')
# """)

st.markdown(md)