"use client";

import { useState, useEffect } from 'react';
import Navbar from '@/components/Navbar';

interface Reply {
    id: number;
    user_name: string;
    content: string;
    created_at: string;
}

interface Post {
    id: number;
    user_name: string;
    title: string;
    content: string;
    created_at: string;
    replies: Reply[];
}

export default function Forum() {
    const [posts, setPosts] = useState<Post[]>([]);
    const [newTitle, setNewTitle] = useState('');
    const [newContent, setNewContent] = useState('');
    const [replyContent, setReplyContent] = useState<Record<number, string>>({});

    const getUserId = () => localStorage.getItem('userId');

    const fetchPosts = () => {
        fetch('http://localhost:8000/api/forum/posts')
            .then(res => res.json())
            .then(data => setPosts(data))
            .catch(console.error);
    };

    useEffect(() => {
        fetchPosts();
    }, []);

    const createPost = async (e: React.FormEvent) => {
        e.preventDefault();
        const uid = getUserId();
        if (!uid) return alert('Please login/register first by going to the homepage.');

        await fetch(`http://localhost:8000/api/forum/posts?user_id=${uid}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ title: newTitle, content: newContent })
        });
        setNewTitle('');
        setNewContent('');
        fetchPosts();
    };

    const createReply = async (e: React.FormEvent, postId: number) => {
        e.preventDefault();
        const uid = getUserId();
        if (!uid) return alert('Please login to reply.');

        const content = replyContent[postId];
        if (!content) return;

        await fetch(`http://localhost:8000/api/forum/posts/${postId}/comments?user_id=${uid}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ content })
        });
        setReplyContent({ ...replyContent, [postId]: '' });
        fetchPosts();
    };

    return (
        <div>
            <Navbar />
            <div style={{ maxWidth: '800px', margin: '0 auto' }}>
                <h1 style={{ marginBottom: '20px' }}>Community Forum</h1>

                <form onSubmit={createPost} className="glass" style={{ padding: '20px', marginBottom: '40px', display: 'flex', flexDirection: 'column', gap: '15px' }}>
                    <h3>Start a Discussion</h3>
                    <input className="input-glass" placeholder="Title" value={newTitle} onChange={e => setNewTitle(e.target.value)} required />
                    <textarea className="input-glass" placeholder="What's on your mind?" value={newContent} onChange={e => setNewContent(e.target.value)} rows={3} required />
                    <button type="submit" className="btn-primary" style={{ alignSelf: 'flex-start' }}>Post</button>
                </form>

                <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
                    {posts.map(post => (
                        <div key={post.id} className="glass" style={{ padding: '20px' }}>
                            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '10px' }}>
                                <h3 style={{ color: 'var(--brand-tertiary)' }}>{post.title}</h3>
                                <small style={{ color: 'var(--text-muted)' }}>Posted by: {post.user_name}</small>
                            </div>
                            <p style={{ marginBottom: '20px' }}>{post.content}</p>

                            {/* Replies */}
                            <div style={{ marginLeft: '20px', borderLeft: '2px solid rgba(255,255,255,0.1)', paddingLeft: '15px' }}>
                                {post.replies.map(r => (
                                    <div key={r.id} style={{ marginBottom: '10px' }}>
                                        <strong>{r.user_name}: </strong> <span style={{ color: 'var(--text-muted)' }}>{r.content}</span>
                                    </div>
                                ))}

                                <form onSubmit={(e) => createReply(e, post.id)} style={{ display: 'flex', gap: '10px', marginTop: '15px' }}>
                                    <input
                                        className="input-glass"
                                        style={{ padding: '8px 12px' }}
                                        placeholder="Write a reply..."
                                        value={replyContent[post.id] || ''}
                                        onChange={e => setReplyContent({ ...replyContent, [post.id]: e.target.value })}
                                    />
                                    <button type="submit" className="btn-primary" style={{ padding: '8px 16px' }}>Reply</button>
                                </form>
                            </div>
                        </div>
                    ))}
                </div>
            </div>
        </div>
    );
}
